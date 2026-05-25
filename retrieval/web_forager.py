"""
retrieval/web_forager.py — [v1.0.0 Sovereign Web Forager]
──────────────────────────────────────────────────────────
Modulo di Web Foraging completo per NeuralVault.

Capacità:
1. Fetch HTTP con fallback Playwright per pagine JS-rendered.
2. HTML Parsing e pulizia del testo con BeautifulSoup.
3. Crawling ricorsivo di sottopagine con depth controllata.
4. OCR su immagini (<img>) e PDF tramite pytesseract + pdfminer.
5. Estrazione strutturata: titolo, meta-description, headings, testo, link.
6. Rate limiting e deduplicazione URL.
7. Output pronto per ingestione in NeuralVault (lista di Dict con text+metadata).
"""

from __future__ import annotations

import re
import time
import random
import hashlib
import asyncio
import urllib.parse
from urllib.parse import urljoin, urlparse, urldefrag
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass, field
from utils.backpressure import backpressure
from utils.proxy_manager import PROXY_MGR
from utils.doh_resolver import DNS_RESOLVER
from retrieval.session_manager import SESSION_MGR
from retrieval.stealth_utils import RefererChainManager, WafSignalDetector
import curl_cffi.requests as requests
from storage.search_mirror import SearchMirrorManager

# ── Dipendenze core ───────────────────────────────────────────────
from curl_cffi import requests as curl_requests
import httpx
import logging

logger = logging.getLogger(__name__)

# ── Dipendenze opzionali (graceful degradation) ───────────────────
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("⚠️ [Forager] beautifulsoup4 non installata. HTML parsing limitato.")

try:
    import playwright.async_api as pw
    from playwright_stealth import Stealth
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    import pytesseract
    from PIL import Image
    import io
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

try:
    from pdfminer.high_level import extract_text as pdf_extract_text
    import io as _io
    HAS_PDF = True
except ImportError:
    HAS_PDF = False


@dataclass
class ForagedPage:
    """Rappresenta una pagina web estratta e pulita."""
    url: str
    title: str
    text: str
    headings: List[str] = field(default_factory=list)
    description: str = ""
    links: List[str] = field(default_factory=list)
    depth: int = 0
    fetch_time: float = field(default_factory=time.time)
    status_code: int = 200
    content_type: str = "text/html"
    images: List[str] = field(default_factory=list) # Raw image URLs
    images_ocr: List[str] = field(default_factory=list)

    def to_chunks(self) -> List[Dict]:
        """
        Trasforma la pagina in chunk pronti per upsert_text().
        Crea chunk separati per heading/sezione quando il testo è lungo.
        """
        chunks = []
        base_meta = {
            "source": self.url,
            "origin": "web_forager",
            "title": self.title,
            "description": self.description,
            "depth": self.depth,
            "fetch_time": self.fetch_time,
        }

        # Chunk principale (testo completo se breve, altrimenti headline + intro)
        if len(self.text) <= 1500:
            chunks.append({"text": f"{self.title}\n\n{self.text}", "metadata": {**base_meta, "chunk": "full"}})
        else:
            # Spezziamo su paragrafi doppi
            paragraphs = [p.strip() for p in self.text.split("\n\n") if len(p.strip()) > 40]
            for i, para in enumerate(paragraphs[:50]):  # Max 50 chunk per pagina
                chunks.append({
                    "text": para,
                    "metadata": {**base_meta, "chunk": f"p{i}"}
                })

        # Chunk OCR da immagini (se presenti)
        for j, ocr_text in enumerate(self.images_ocr):
            if len(ocr_text.strip()) > 30:
                chunks.append({
                    "text": f"[OCR da immagine] {ocr_text}",
                    "metadata": {**base_meta, "chunk": f"ocr_{j}", "type": "ocr"}
                })

        return chunks


class SovereignWebForager:
    """
    Motore di Web Foraging Sovrano per NeuralVault.
    Trasforma qualsiasi URL in conoscenza strutturata pronta per l'ingestione.
    """
    _network_offline = False
    _last_offline_time = 0.0

    def __init__(
        self,
        max_depth: int = 12,
        max_pages: int = 25000,
        rate_limit_sec: float = 0.2,
        same_domain_only: bool = True,
        timeout_sec: float = 180.0,
        use_playwright: bool = False,
    ):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.rate_limit = rate_limit_sec
        self.same_domain_only = same_domain_only
        self.timeout = timeout_sec
        self.use_playwright = use_playwright and HAS_PLAYWRIGHT
        self.session = curl_requests.AsyncSession()

        self._visited: Set[str] = set()
        self.proposals: List[Dict] = [] # Argomenti per approfondimento esterno
        
        # 🛡️ [v9.5] Circuit Breaker State
        self._engine_status = {
            "Google": {"failures": 0, "last_error": 0, "open": False},
            "DuckDuckGo": {"failures": 0, "last_error": 0, "open": False},
            "Brave": {"failures": 0, "last_error": 0, "open": False},
            "Startpage": {"failures": 0, "last_error": 0, "open": False},
            "SearXNG": {"failures": 0, "last_error": 0, "open": False}
        }
        self._breaker_threshold = 3
        self._breaker_cooldown = 300 # 5 minuti
        
        # 🏛️ [v9.7] Search Mirror: Local-First Intelligence
        self.mirror = SearchMirrorManager()

    @staticmethod
    def refine_query(query: str, max_len: int = 180) -> str:
        """
        [Query Optimizer v1.2 APEX]
        Pulisce e ottimizza la query per i motori di ricerca.
        """
        if not query: return ""
        
        # 1. Rimuove path (es: /Users/.../file.py)
        query = re.sub(r'/[a-zA-Z0-9._/-]+/[a-zA-Z0-9._-]+\.[a-z]{2,4}', '', query)
        
        # 2. Rimuove frammenti di log/esadecimali/indirizzi di memoria
        query = re.sub(r'0x[0-9a-fA-F]+', '', query)
        query = re.sub(r'[a-fA-F0-9]{32,}', '', query) # Long hex hashes
        
        # 3. Se somiglia a codice, estraiamo i termini salienti
        if any(c in query for c in "()[]{}.->"):
            # Filtriamo parole comuni di programmazione se troppo brevi o noise
            words = re.findall(r'[a-zA-Z0-9_]{3,}', query)
            # Stopwords tecniche comuni da ignorare nella query di ricerca
            tech_stopwords = {"self", "this", "null", "none", "true", "false", "void", "return", "import", "from", "class", "def"}
            filtered_words = [w for w in words if w.lower() not in tech_stopwords]
            query = " ".join(filtered_words[:10])
        
        # 4. Pulizia caratteri speciali residui
        query = re.sub(r'[^\w\s\-\.\?]', ' ', query)
        query = " ".join(query.split())
        
        # 5. Troncamento intelligente
        if len(query) > max_len:
            query = query[:max_len].rsplit(' ', 1)[0]
            
        return query.strip()

    async def search(self, query: str, num_results: int = 3):
        """
        [v9.5] Search Fabric: Cascades through multiple sources with progressive fallback.
        1. Mainstream (Google/DDG)
        2. Sovereign (SearXNG/YaCy)
        3. Internal Insight Synthesis (RAG)
        """
        clean_query = self.refine_query(query)
        if not clean_query: return
        
        print(f"🔍 [Forager/Search] Query: '{clean_query}' | Initializing Multi-Level Fallback...")
        
        # Livello 1 & 2: Stealth Search (Google, DDG, Brave, SearXNG)
        stealth_results = await self.stealth_search(clean_query, limit=num_results)
        found_urls = stealth_results.get("urls", [])
        
        if found_urls:
            for url in found_urls:
                async for page in self.forage(url) :
                    yield page
            return

        # Livello 3: Internal Insight Synthesis (Sovereign Fallback)
        print("⚠️ [Forager] Web retrieval failed or blocked. Activating Internal Insight Synthesis...")
        synthetic_page = await self._internal_synthesis(clean_query)
        if synthetic_page:
            yield synthetic_page

    def _normalize_url(self, url: str) -> str:
        """Pulisce e normalizza l'URL, rimuovendo caratteri illegali e spazi."""
        if not url: return ""
        # Rimuove ritorni a capo e caratteri non stampabili che causano InvalidURL
        url = "".join(ch for ch in url if ch.isprintable() and not ch.isspace()).strip()
        url, _ = urldefrag(url)
        return url.rstrip("/")

    def _is_valid_url(self, url: str, base_domain: str) -> bool:
        """Filtro Sovrano: Valida URL e previene l'ingestione di 'Useless Info' (Indici, Archivi, Search)."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            
            # 1. Check Dominio
            if self.same_domain_only:
                target = parsed.netloc.lower()
                base = base_domain.lower()
                base_clean = base.replace("www.", "")
                if not (target == base or target.endswith(f".{base_clean}") or target == base_clean):
                    return False
            
            # 2. Blacklist 'Useless Info' (v1.0.5)
            # Evitiamo indici alfabetici, pagine di ricerca, tag clouds e archivi piatti
            blacklist = ["/genindex", "/search", "/tag/", "/archive", "/category/", "/contents.html", "google-search", "?s=", "&s="]
            if any(p in url.lower() for p in blacklist):
                return False

            # 3. Check Estensioni spazzatura
            if any(url.lower().endswith(ext) for ext in [".zip", ".pdf", ".docx", ".exe", ".bin"]):
                return False
            
            return True
        except Exception:
            return False

    async def _parse_html(self, html: str, url: str) -> ForagedPage:
        if not HAS_BS4:
            return ForagedPage(url=url, title="Unknown (BS4 Missing)", text=html[:5000])

        soup = BeautifulSoup(html, "html.parser")
        
        # 🔗 Estrazione link PRIMA della decomposizione (v1.0.2 Fix Stall)
        links = []
        for a in soup.find_all("a", href=True):
            links.append(urljoin(url, a["href"]))

        # Selettori CSS da ignorare (Pubblicità, Navigazione, Legal, etc.)
        ad_selectors = ["footer", "nav", "aside", ".ads", ".banner", ".sidebar", ".cookie", ".social", ".menu", ".breadcrumb", "script", "style", "iframe", "header"]
        for selector in ad_selectors:
            for element in soup.select(selector):
                element.decompose()

        main_content = soup.find("main") or soup.find("article") or soup.find(id="content") or soup.find(class_="body") or soup.body
        if main_content:
            # Preserva struttura paragrafo ed elenchi
            for tag in main_content.find_all(["p", "li", "h1", "h2", "h3", "h4", "blockquote", "td", "th"]):
                tag.string = "\n" + tag.get_text(separator=" ", strip=True) + "\n"
            raw_text = main_content.get_text(separator="\n")
        else:
            raw_text = soup.get_text(separator="\n")

        # Pulizia aggressiva del testo e rimozione frammenti troppo brevi (noise)
        lines = [line.strip() for line in raw_text.splitlines()]
        lines = [line for line in lines if len(line) > 15]
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        # Estrazione metadati
        title = (soup.title.string if soup.title else "Untitled Page").strip()
        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "").strip()
        
        headings = [h.get_text().strip() for h in soup.find_all(["h1", "h2", "h3"])]

        # Creazione pagina foraggiata con limiti sovrani (50k char)
        return ForagedPage(
            url=url,
            title=title,
            text=text[:50000],
            headings=headings,
            description=description,
            links=links,
            images=[urljoin(url, img["src"]) for img in soup.find_all("img", src=True)]
        )

    async def _ocr_images(self, soup: "BeautifulSoup", base_url: str) -> List[str]:
        """Esegue OCR sulle immagini reali della pagina, filtrando icone e loghi."""
        if not HAS_OCR:
            return []

        ocr_results = []
        # Cerchiamo solo immagini coerenti (almeno 100px di larghezza potenziale)
        images = soup.find_all("img", src=True)
        valid_images = []
        for img in images:
            src = img["src"].lower()
            # Heuristic per evitare pubblicità/icone
            if any(x in src for x in ["icon", "logo", "banner", "adserver", "pixel", "tracker", "sprite"]):
                continue
            valid_images.append(img)

        for img in valid_images[:15]: # Limite per efficienza
            img_url = urljoin(base_url, img["src"])
            try:
                # Tentativo di recupero metadati (alt text) come fallback prima di OCR pesante
                alt_text = img.get("alt", "").strip()
                if len(alt_text) > 40:
                    ocr_results.append(f"[ALT-TAG]: {alt_text}")
                    continue

                resp = await self._client.get(img_url, timeout=5.0)
                if "image" in resp.headers.get("content-type", ""):
                    pil_img = Image.open(io.BytesIO(resp.content))
                    # Check dimensioni minime per evitare noise
                    if pil_img.width < 100 or pil_img.height < 100:
                        continue
                    text = pytesseract.image_to_string(pil_img, lang="ita+eng").strip()
                    
                    def _is_real_text(t):
                        words = t.split()
                        if len(words) < 5: return False
                        letters = sum(1 for c in t if c.isalpha())
                        return letters / max(len(t), 1) > 0.6
                        
                    if len(text) > 20 and _is_real_text(text):
                        ocr_results.append(text)
                    else:
                        # [v3.0] Fallback to Vision Model for architectural diagrams/UI
                        try:
                            import base64
                            import httpx
                            import json
                            import os
                            
                            # Legge il modello vision dalle impostazioni (se esiste) o usa moondream
                            vision_model = "moondream"
                            try:
                                if os.path.exists("vault_settings.json"):
                                    with open("vault_settings.json", "r") as sf:
                                        vision_model = json.load(sf).get("multimodal", "moondream")
                            except: pass
                            
                            buffer = io.BytesIO()
                            pil_img.convert('RGB').save(buffer, format="JPEG", quality=85)
                            img_b64 = base64.b64encode(buffer.getvalue()).decode()
                            
                            prompt = "Sei un assistente tecnico avanzato. Descrivi sinteticamente cosa mostra questa immagine. Concentrati su diagrammi, grafici, architetture, relazioni o informazioni salienti. Rispondi con massimo 3 frasi."
                            async with httpx.AsyncClient(timeout=20.0) as c:
                                payload = {
                                    "model": vision_model,
                                    "prompt": prompt,
                                    "images": [img_b64],
                                    "stream": False,
                                    "options": {"temperature": 0.1}
                                }
                                v_resp = await c.post("http://127.0.0.1:11434/api/generate", json=payload)
                                if v_resp.status_code == 200:
                                    vlm_text = v_resp.json().get("response", "").strip()
                                    if vlm_text:
                                        ocr_results.append(f"[VLM Vision] {vlm_text}")
                        except Exception as ve:
                            pass
            except Exception:
                pass

        return ocr_results

    async def _fetch_page(self, url: str, proxy_config: Optional[dict] = None) -> str:
        """[v9.7 GHOST PROTOCOL] Recupero stealth con DoH, Sessioni e WAF Detection."""
        if SovereignWebForager._network_offline:
            if time.time() - SovereignWebForager._last_offline_time < 300:
                logger.info(f"📡 [Forager] System is offline. Skipping fetch for {url}")
                return ""
            else:
                SovereignWebForager._network_offline = False

        try:
            from urllib.parse import urlparse
            hostname = urlparse(url).hostname
            
            # 1. DNS Stealth: Pre-volo DoH
            await DNS_RESOLVER.resolve(hostname)

            # 2. Session & Referer Injection
            cookies = SESSION_MGR.get_session_cookies(hostname)
            referer = RefererChainManager.get_referer_for_query(hostname)
            
            # 3. Header Ordering Deterministic (M1 Optimized)
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8",
                "Referer": referer,
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="124", "Google Chrome";v="124"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"macOS"',
                "Upgrade-Insecure-Requests": "1"
            }

            # Human Jitter: Ritardo log-normale prima di scaricare
            await asyncio.sleep(random.lognormvariate(0.5, 0.2))

            # 4. Request execution via curl_cffi (Wrapped in wait_for to prevent libcurl DNS freeze)
            resp = await asyncio.wait_for(
                self.session.get(
                    url, 
                    proxy=proxy_config["url"] if proxy_config else None,
                    impersonate="chrome124",
                    cookies=cookies,
                    headers=headers,
                    timeout=20.0
                ),
                timeout=25.0
            )
            
            # 5. WAF Signal Analysis
            analysis = WafSignalDetector.analyze(resp.text, resp.headers)
            if analysis["risk_level"] == "HIGH":
                logger.warning(f"🚨 [Stealth] WAF Signal Detected on {hostname}: {analysis['signals']}")
                if proxy_config:
                    PROXY_MGR.report_error(proxy_config["id"])
                
                raise Exception(f"WAF-Block-Detected: {analysis['signals']}")

            # 6. Session Update
            SESSION_MGR.update_session(hostname, resp.cookies.get_dict())
            
            if resp.status_code == 200:
                ct = resp.headers.get("content-type", "").lower()
                if "html" in ct:
                    return resp.text
                elif "pdf" in ct and HAS_PDF:
                    return self._extract_pdf(resp.content)
            
            return ""
            
        except Exception as e:
            if "WAF-Block" not in str(e):
                logger.warning(f"⚠️ [Forager] Stealth Fetch Warning: {e}")
            else:
                logger.warning(f"🛡️ [Forager] Blocked by WAF: {e}")
            
            # [v9.8] Try high-speed Proxy-Fallback via Jina Reader first to bypass local timeouts/blocks
            jina_content = await self._fetch_with_jina(url)
            if jina_content:
                return jina_content
                
            # Fallback finale a Playwright
            if HAS_PLAYWRIGHT:
                return await self._fetch_with_playwright(url)
            return ""

    async def _fetch_with_jina(self, url: str) -> Optional[str]:
        """Utilizza r.jina.ai per estrarre markdown pulito da pagine JS-heavy."""
        jina_url = f"https://r.jina.ai/{url}"
        try:
            headers = {"X-Return-Format": "markdown"}
            async with httpx.AsyncClient(headers=headers, timeout=18.0, follow_redirects=True) as client:
                resp = await client.get(jina_url)
                if resp.status_code == 200:
                    print(f"🚀 [Forager] Jina Reader SUCCESS for {url[:50]}...")
                    return resp.text
        except Exception: pass
        return None

    def _extract_pdf(self, content: bytes) -> str:
        """Estrae testo da PDF."""
        if not HAS_PDF:
            return ""
        try:
            text = pdf_extract_text(_io.BytesIO(content))
            return text[:50000] if text else ""
        except Exception:
            return ""

    async def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """Fallback con Playwright per contenuti JS-rendered (React, Vue, etc.)."""
        if not HAS_PLAYWRIGHT:
            return None
        try:
            import os
            # [Fix EACCES mkdtemp] Force Playwright to use a safe temp directory on macOS
            original_tmp = os.environ.get("TMPDIR")
            os.environ["TMPDIR"] = "/tmp"
            
            async with pw.async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                
                # Restore original TMPDIR immediately after launch
                if original_tmp: os.environ["TMPDIR"] = original_tmp
                else: del os.environ["TMPDIR"]
                
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                page = await context.new_page()
                
                # ⚡ [Optimization v16.2] Block useless heavy resources to speed up load
                async def safe_abort(route):
                    try:
                        await route.abort()
                    except Exception:
                        pass
                await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,css,woff,woff2,ttf}", safe_abort)
                
                await Stealth().apply_stealth_async(page)
                
                try:
                    # Aumentiamo il timeout a 45s per siti molto lenti
                    await page.goto(url, timeout=45000)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=8000)
                    except: pass # Se networkidle fallisce, prendiamo quello che c'è
                    
                    html = await page.content()
                finally:
                    # Gracefully clean up route handlers and close playwright components
                    try:
                        await page.unroute("**/*.{png,jpg,jpeg,gif,webp,svg,css,woff,woff2,ttf}", safe_abort)
                    except Exception:
                        pass
                    # Yield control to let any pending/cancelling routing tasks complete gracefully
                    await asyncio.sleep(0.05)
                    try:
                        await page.close()
                    except Exception:
                        pass
                    try:
                        await context.close()
                    except Exception:
                        pass
                    try:
                        await browser.close()
                    except Exception:
                        pass
                
                return html
        except Exception as e:
            print(f"⚠️ [Forager] Playwright fallito per {url}: {e}")
            return None

    async def stealth_search(self, query: str, limit: int = 10, zen: bool = False) -> Dict[str, Any]:
        """
        [Sovereign Stealth Search v4.0 - Mirror Augmented]
        Esegue una ricerca web multi-engine parallela con controllo Local-First (Mirror).
        """
        import time
        start_time = time.time()

        # Check if we are currently flagged as offline (cooldown 300 seconds)
        if SovereignWebForager._network_offline:
            if time.time() - SovereignWebForager._last_offline_time < 300:
                print(f"📡 [Forager/Stealth] Network is flagged OFFLINE. Bypassing external search for '{query}'...")
                cached = self.mirror.get_cached_results(query, max_age_hours=48)
                if cached:
                    print(f"🏛️ [Forager/Mirror] Local hit for '{query}' during offline mode.")
                    return {"urls": [r["url"] for r in cached], "ai_content": "Source: SearchMirror (Local Cache)"}
                return {"urls": [], "ai_content": "Offline Mode"}
            else:
                SovereignWebForager._network_offline = False
        
        # 🏛️ [v9.7] STEP 1: Check Local Mirror (Local-First)
        cached = self.mirror.get_cached_results(query, max_age_hours=48)
        if cached and len(cached) >= limit:
            print(f"🏛️ [Forager/Mirror] Local hit for '{query}'. Returning {len(cached)} cached sources.")
            return {"urls": [r["url"] for r in cached], "ai_content": "Source: SearchMirror (Local Cache)"}

        print(f"🕵️ [Forager/Stealth] Diagnostic Harvest initiated for: '{query}'")
        urls = []
        
        engines = {
            "DuckDuckGo": f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}",
            "Google": f"https://www.google.com/search?q={urllib.parse.quote(query)}&gbv=1",
            "Brave": f"https://search.brave.com/search?q={urllib.parse.quote(query)}",
            "Startpage": f"https://www.startpage.com/do/search?query={urllib.parse.quote(query)}"
        }

        # [v25.6] Parallel execution with Circuit Breaker and curl_cffi
        async def protected_fetch(name, url):
            # Check Circuit Breaker
            status = self._engine_status.get(name)
            if status and status["open"]:
                if time.time() - status["last_error"] > self._breaker_cooldown:
                    status["open"] = False
                    status["failures"] = 0
                else:
                    return []

            try:
                # [v9.5] Impersonificazione TLS e Proxy Sovrano
                config = PROXY_MGR.get_session_config()
                async with curl_requests.AsyncSession(
                    impersonate=config["impersonate"],
                    proxies=config["proxies"]
                ) as session:
                    await asyncio.sleep(random.uniform(0.5, 1.5)) # Jitter pre-engine
                    resp = await session.get(url, timeout=12.0)
                    if resp.status_code == 200:
                        self._engine_status[name]["failures"] = 0
                        soup = BeautifulSoup(resp.text, "html.parser")
                        results = []
                        
                        # Cerchiamo di estrarre Titolo e URL (migliorato v9.7)
                        for a in soup.find_all("a", href=True):
                            href = a["href"]
                            title = a.get_text().strip()
                            
                            if "/url?q=" in href: href = href.split("/url?q=")[1].split("&")[0]
                            elif "uddg=" in href: href = href.split("uddg=")[1].split("&")[0]
                            try: href = urllib.parse.unquote(href)
                            except: pass
                            
                            if href.startswith("http") and not any(x in href for x in ["google", "duckduckgo", "bing", "brave", "startpage"]):
                                clean_url = href.split("?")[0] if "?" in href and "url?q=" not in href else href
                                results.append({"url": clean_url, "title": title if title else "Web Resource"})
                        return results
                    else:
                        raise Exception(f"HTTP {resp.status_code}")
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "Too Many Requests" in err_msg:
                    logger.info(f"ℹ️ [Forager/Search] Engine {name} rate limited (HTTP 429).")
                else:
                    logger.warning(f"⚠️ [Forager/Search] Engine {name} failed: {e}")
                    
                self._engine_status[name]["failures"] += 1
                self._engine_status[name]["last_error"] = time.time()
                if self._engine_status[name]["failures"] >= self._breaker_threshold:
                    self._engine_status[name]["open"] = True
                    print(f"🚨 [Breaker] Engine {name} OPEN (Isolato per 5m) a causa di: {e}")
                    # Assumiamo PROXY_MGR sia globale e inizializzato
                    try:
                        if hasattr(PROXY_MGR, 'use_tor') and PROXY_MGR.use_tor:
                            asyncio.create_task(PROXY_MGR.rotate_tor_identity())
                    except: pass
                return []

        async def fetch_with_timeout(name, url):
            try:
                return await asyncio.wait_for(protected_fetch(name, url), timeout=15.0)
            except asyncio.TimeoutError:
                print(f"⚠️ [Forager/Stealth] Engine {name} timed out (>15s).")
                self._engine_status[name]["failures"] += 1
                self._engine_status[name]["last_error"] = time.time()
                if self._engine_status[name]["failures"] >= self._breaker_threshold:
                    self._engine_status[name]["open"] = True
                    print(f"🚨 [Breaker] Engine {name} OPEN (Isolato per 5m) a causa di Timeout")
                return []
            except Exception as e:
                logger.error(f"❌ [Forager/Search] Timeout wrapper exception for {name}: {e}")
                return []

        tasks = [fetch_with_timeout(name, url) for name, url in engines.items()]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        for r in raw_results:
            if isinstance(r, list):
                all_results.extend(r)
        
        # Unifica per URL
        unique_results = {}
        for r in all_results:
            if r["url"] not in unique_results:
                unique_results[r["url"]] = r
        
        harvested_list = list(unique_results.values())[:limit]
        harvested_urls = [r["url"] for r in harvested_list]
        
        # --- [v9.7] Mirror Enrichment ---
        if harvested_list:
            self.mirror.add_results(query, "Swarm-Stealth", harvested_list)
        else:
            # If no URLs found, and we have multiple engine failures, trigger network offline flag
            failures_count = sum(1 for status in self._engine_status.values() if status["failures"] > 0 or status["open"])
            if failures_count >= len(engines) - 1:
                print(f"🚨 [Forager/Stealth] Multiple search engines failed/timed out. Flagging system as OFFLINE for 5 minutes.")
                SovereignWebForager._network_offline = True
                SovereignWebForager._last_offline_time = time.time()
        
        total_dt = time.time() - start_time
        print(f"✅ [Forager/Stealth] Harvested {len(harvested_urls)} sources in {total_dt:.2f}s.")
        return {"urls": harvested_urls, "ai_content": ""}

    async def _internal_synthesis(self, query: str) -> Optional[ForagedPage]:
        """
        [v9.5] Sovereign Fallback: Generates a synthetic page from local Vault knowledge.
        Requires the engine to be accessible (usually passed via Skywalker/Yoda).
        """
        # Nota: Questa funzione assume che l'engine sia stato iniettato 
        # o che possiamo interrogarlo tramite un'interfaccia globale.
        # Per ora creiamo una pagina segnaposto che descrive la necessità di fallback locale.
        return ForagedPage(
            url="sovereign://internal_synthesis",
            title=f"Internal Insight: {query}",
            text=f"Il foraging web per '{query}' è stato interrotto o bloccato. "
                 f"Attivazione della sintesi neurale basata sui nodi esistenti nel Vault.",
            description="Sintesi generata localmente causa blocco motori di ricerca esterni."
        )

    async def forage(self, start_url: str):
        """
        Punto di ingresso principale.
        Crawla l'URL di partenza e le sue sottopagine fino a max_depth.
        Yields ForagedPage real-time.
        """
        start_url = self._normalize_url(start_url)
        base_domain = urlparse(start_url).netloc

        # Definiamo queue e visited come locali per isolamento dei thread concorrenti (v9.8)
        queue: List[tuple[str, int]] = [(start_url, 0)]  # (url, depth)
        visited: Set[str] = set()

        # Manteniamo referenze d'istanza per compatibilità all'indietro
        self.queue = queue
        self._visited = visited

        print(f"🕸️ [Forager] Avvio forage: {start_url} (max_depth={self.max_depth}, max_pages={self.max_pages})")
        
        pages_count = 0
        try:
            while queue and pages_count < self.max_pages:
                url, depth = queue.pop(0)
                norm_url = self._normalize_url(url)

                if norm_url in visited:
                    continue
                
                # --- BACKPRESSURE PROTOCOL (Gap #2) ---
                throttle = backpressure.get_throttle_factor()
                if throttle < 0.2:
                    await backpressure.async_wait_if_clogged()
                elif throttle < 0.5:
                    print(f"⏳ [Backpressure] Throttling forager (factor: {throttle:.2f})...")
                    await asyncio.sleep(2.0 * (1.1 - throttle))
                
                visited.add(norm_url)

                # Telemetria in tempo reale: Calcolo progresso
                current_idx = pages_count + 1
                progress_pct = (current_idx / self.max_pages) * 100 if self.max_pages > 0 else 0
                
                print(f"📄 [Forager] [{current_idx}/{self.max_pages}] {progress_pct:.1f}% | Memoria Synaptica: {norm_url[:60]}...")

                html = await self._fetch_page(norm_url)
                if not html:
                    continue

                page = await self._parse_html(html, norm_url)
                page.depth = depth

                pages_count += 1
                yield page

                # Aggiungi link validi alla coda (solo se non al massimo depth)
                if depth < self.max_depth:
                    for link in page.links:
                        norm_link = self._normalize_url(link)
                        if (norm_link not in visited
                                and self._is_valid_url(link, base_domain)
                                and len(queue) < self.max_pages * 3):
                            queue.append((link, depth + 1))

                # Rate limiting cortese
                await asyncio.sleep(self.rate_limit)
        finally:
            print(f"✅ [Forager] Completato: {pages_count} pagine estratte da {base_domain}")

    def forage_sync(self, start_url: str) -> List[ForagedPage]:
        """Versione sincrona per utilizzo da script Python."""
        async def _collect():
            return [p async for p in self.forage(start_url)]
        return asyncio.run(_collect())


def forage_to_chunks(
    start_url: str,
    max_depth: int = 2,
    max_pages: int = 20,
    same_domain_only: bool = True,
    use_playwright: bool = False,
) -> List[Dict]:
    """
    Funzione di alto livello: dato un URL restituisce tutti i chunk
    pronti per vault.upsert_text().

    Esempio:
        chunks = forage_to_chunks("https://docs.mysite.com", max_depth=2)
        for c in chunks:
            vault.upsert_text(c["text"], metadata=c["metadata"])
    """
    forager = SovereignWebForager(
        max_depth=max_depth,
        max_pages=max_pages,
        same_domain_only=same_domain_only,
        use_playwright=use_playwright,
    )
    pages = forager.forage_sync(start_url)
    all_chunks = []
    for page in pages:
        all_chunks.extend(page.to_chunks())
    return all_chunks
