import logging
import asyncio
import threading
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pathlib import Path
import time
import json
import os

# 🛡️ [Security] Filter only authorized user
class TelegramSovereignLink:
    def __init__(self, orchestrator, token: str, authorized_user_id: str):
        self.orch = orchestrator
        self.token = token
        self.authorized_user_id = str(authorized_user_id)
        self.app = None
        self.loop = None
        self._thread = None
        self._is_running = False
        
        # Silenzia i log di telegram per non inquinare il terminale di NeuralVault
        logging.getLogger("telegram").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

    def is_authorized(self, update: Update):
        if not self.authorized_user_id: return True # Se non impostato, chiunque può accedere (Sconsigliato)
        return str(update.effective_user.id) == self.authorized_user_id

    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.is_authorized(update):
            u_id = update.effective_user.id
            u_name = update.effective_user.username or update.effective_user.first_name
            print(f"🚫 [Telegram] Accesso negato per {u_name} (ID: {u_id}). Imposta questo ID nelle impostazioni per autorizzarlo.")
            await update.message.reply_text(f"🚫 Accesso Negato.\nIl tuo ID è: `{u_id}`\nComunicalo al Sovrano per essere autorizzato.", parse_mode='Markdown')
            return
        
        user_name = update.effective_user.first_name
        welcome_msg = (
            f"🚀 **NeuralVault Sovereign Link v1.0**\n\n"
            f"Bentornato, {user_name}. Il tuo Sciame è operativo.\n"
            "Usa il menu o i comandi per interagire con la Nebula.\n\n"
            "📜 **/status** - Telemetria Real-time\n"
            "🧠 **/query [testo]** - Interroga il Vault\n"
            "🐝 **/agents** - Stato degli Agenti\n"
            "🌀 **/evolution** - Suggerimenti evolutivi\n"
            "🛡️ **/mode** - Cambia Modalità (Evolution/Research)"
        )
        
        keyboard = [
            [InlineKeyboardButton("📊 Status", callback_data="status"), InlineKeyboardButton("🧠 Query", callback_data="query_prompt")],
            [InlineKeyboardButton("🐝 Agenti", callback_data="agents"), InlineKeyboardButton("🌀 Evolution", callback_data="evolution")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def status_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.is_authorized(update): return
        
        report = self.orch.get_orchestra_report()
        health = report.get("health_score", 0)
        agents = report.get("agents", {})
        
        status_msg = (
            f"📊 **TELEMETRIA VAULT**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🏥 **Health Score:** {health}%\n"
            f"💎 **Nodi Attivi:** {len(self.orch.vault._nodes)}\n"
            f"🌀 **Modalità:** {'Evolution' if self.orch.evolution_active else 'Research'}\n\n"
            f"**Attività Agenti:**\n"
        )
        
        # Aggreghiamo i contatori principali
        for aid, data in agents.items():
            icon = "✅" if "Idle" not in str(data.get("status")) else "💤"
            if aid == "FS-77":
                status_msg += f"🚀 FS-77 SkyWalker: {data.get('web_hits', 0)} hits | {data.get('nodes_forged', 0)} nodi\n"
            elif aid == "CB-003":
                status_msg += f"🔗 CB-003 Bridger: {data.get('bridges', 0)} ponti\n"
            elif aid == "SN-008":
                 status_msg += f"🐍 SN-008 Snake: {data.get('found', 0)} trovati\n"
        
        await update.message.reply_text(status_msg, parse_mode='Markdown')

    async def query_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.is_authorized(update): return
        
        query_text = " ".join(context.args)
        if not query_text:
            await update.message.reply_text("💡 Scrivi la tua domanda dopo il comando. Es: `/query intelligenza artificiale`", parse_mode='Markdown')
            return
        
        processing_msg = await update.message.reply_text("🔍 *Interrogazione Nebula in corso...*", parse_mode='Markdown')
        
        # [v4.1.9] PRIORITY SHIFT: Sospensione processi background
        self.orch.set_priority_shift(True)
        
        start_time = time.time()
        try:
            # 1. Espansione Query via Lab (v4.1.5)
            expanded_query = await self.orch.expand_query(query_text)
            
            # 2. Ricerca nel Vault (Aumento top_k per visione d'insieme)
            results = await self.orch.vault.query(expanded_query, top_k=15)
            
            if not results:
                results = await self.orch.vault.query(query_text, top_k=10)
            
            if not results:
                await processing_msg.edit_text("📭 Nessun risultato trovato nel Vault per questa ricerca.")
                return

            # 3. Preparazione Contesto & Filtro Rumore (v4.1.7)
            context_text = ""
            sources_seen = set()
            for r in results:
                source = r.node.metadata.get('source', 'Unknown')
                if "BACKUP" in source and len(results) > 5: continue 
                
                clean_text = str(r.node.text).replace('*', '').replace('_', '').replace('`', '')
                context_text += f"\n[{source}]: {clean_text}\n"
                sources_seen.add(source)

            await processing_msg.edit_text("🧠 *Sintesi Neurale in corso (Visione Globale)...*", parse_mode='Markdown')

            # 4. Generazione Risposta via LLM (Ollama)
            model_name = self.orch.settings.get("chat_mediator", "llama3.2")
            base_url = self.orch.settings.get("ollama_url", "http://127.0.0.1:11434")
            
            prompt = f"""
            Sei il Sovrano di NeuralVault, un'intelligenza artificiale avanzata con accesso a un vault di conoscenza tecnica.
            Il tuo compito è rispondere alla DOMANDA dell'utente in modo preciso, completo e professionale, basandoti ESCLUSIVAMENTE sul CONTESTO fornito.
            
            Se il contesto contiene informazioni tecniche, codice o architetture, usali per fornire una risposta dettagliata.
            Se non trovi informazioni specifiche nel contesto, ammettilo sinceramente ma cerca di estrapolare quanto possibile dai frammenti presenti.
            
            CONTESTO:
            {context_text}
            
            DOMANDA:
            {query_text}
            
            RISPOSTA (in Italiano, tono professionale, struttura a punti se necessario):
            """
            
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{base_url}/api/generate", json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.4}
                }, timeout=300.0)
                
                if resp.status_code == 200:
                    answer = resp.json().get("response", "Errore nella generazione della risposta.")
                    
                    # 5. Calcolo Metriche
                    duration = time.time() - start_time
                    footer = f"\n\n📚 **Fonti Principali:** {', '.join(list(sources_seen)[:4])}"
                    telemetry = f"\n\n⚡ **Sovereign Metrics:**\n• Model: `{model_name}`\n• Response Time: `{duration:.2f}s`"
                    
                    try:
                        await processing_msg.edit_text(answer + footer + telemetry, parse_mode='Markdown')
                    except:
                        await processing_msg.edit_text(answer + footer + telemetry)
                else:
                    await processing_msg.edit_text(f"❌ Errore durante la sintesi LLM (Ollama status: {resp.status_code})")
                    
        except Exception as e:
            err_msg = str(e) if str(e) else "Errore sconosciuto (probabile timeout o disconnessione LLM)"
            print(f"🚨 [Telegram Query Error] {err_msg}")
            await processing_msg.edit_text(f"🚨 Errore durante l'interrogazione: `{err_msg}`", parse_mode='Markdown')
        finally:
            # [v4.1.9] Ripristino processi background
            self.orch.set_priority_shift(False)

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """🚀 [v1.1] Silenzia i crash di rete ripetitivi."""
        err = context.error
        err_str = str(err)
        
        # Se è un errore di connessione noto, stampiamo un avviso sintetico solo una volta ogni tanto
        if "ConnectError" in err_str or "nodename nor servname" in err_str:
            if not hasattr(self, '_last_conn_err') or time.time() - self._last_conn_err > 300:
                print("📡 [Telegram] Link in standby: Host non raggiungibile (Modalità Offline attiva).")
                self._last_conn_err = time.time()
            return
            
        print(f"⚠️ [Telegram] Errore imprevisto: {err}")

    async def agents_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.is_authorized(update): return
        
        report = self.orch.get_orchestra_report()
        agents = report.get("agents", {})
        
        msg = "🐝 **STATO SCIAME AGENTI**\n\n"
        for aid, data in agents.items():
            status = data.get("status", "Unknown")
            identity = data.get("identity", {})
            name = identity.get("name", aid)
            msg += f"• **{aid}** ({name}): `{status}`\n"
            
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def evolution_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.is_authorized(update): return
        
        advice = self.orch.evolution_advise.get_all_suggestions()
        if not advice:
            await update.message.reply_text("🌀 Nessun suggerimento evolutivo pendente.")
            return
        
        msg = "🌀 **SUGGERIMENTI EVOLUTIVI**\n\n"
        for adv in advice[-3:]: # Mostra gli ultimi 3
            msg += f"📄 **File:** `{adv.get('file')}`\n"
            msg += f"💡 **Proposta:** {adv.get('content')}\n"
            msg += f"⚠️ **Impatto:** {adv.get('impact')}\n"
            msg += "━━━━━━━━━━━━━━━\n"
            
        await update.message.reply_text(msg, parse_mode='Markdown')

    def run(self):
        """Avvia il bot in un loop asincrono dedicato."""
        self._is_running = True
        self.app = Application.builder().token(self.token).build()
        
        # Gestore Errori per evitare inondazioni nel terminale
        self.app.add_error_handler(self.error_handler)
        
        # Comandi
        self.app.add_handler(CommandHandler("start", self.start_cmd))
        self.app.add_handler(CommandHandler("status", self.status_cmd))
        self.app.add_handler(CommandHandler("query", self.query_cmd))
        self.app.add_handler(CommandHandler("agents", self.agents_cmd))
        self.app.add_handler(CommandHandler("evolution", self.evolution_cmd))
        
        try:
            self.app.run_polling(drop_pending_updates=True, stop_signals=False)
        except Exception as e:
            if "nodename nor servname provided" in str(e) or "ConnectError" in str(e):
                print("❌ [Telegram] Connessione Fallita: Host non raggiungibile.")
                print("💡 Verifica la tua connessione internet o i DNS. Il bot funzionerà in modalità OFFLINE (Disconnesso).")
            else:
                print(f"❌ [Telegram] Errore critico durante il polling: {e}")
            self._is_running = False

    def stop(self):
        """Ferma il bot in modo pulito e rilascia la connessione."""
        if self.app:
            print("🤖 [Telegram] Spegnimento Sovereign Link...")
            self._is_running = False
            import asyncio
            import time
            try:
                # v20+ richiede gestione asincrona. Usiamo un approccio che evita conflitti di loop.
                async def _async_stop():
                    if self.app.updater and self.app.updater.running:
                        await self.app.updater.stop()
                    await self.app.stop()
                    await self.app.shutdown()
                
                try:
                    # Se siamo già in un loop (raro in questo thread, ma possibile)
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        threading.Thread(target=lambda: asyncio.run(_async_stop())).start()
                    else:
                        loop.run_until_complete(_async_stop())
                except RuntimeError:
                    # Nessun loop nel thread corrente (caso normale per thread daemon)
                    asyncio.run(_async_stop())

                time.sleep(1.5)
                print("✅ [Telegram] Link disconnesso correttamente.")
            except Exception as e:
                print(f"⚠️ [Telegram] Errore durante lo spegnimento: {e}")

def start_telegram_bridge(orchestrator, settings, existing_bridge=None):
    """Factory per avviare o riavviare il bot in un thread separato."""
    token = settings.get("telegram_token")
    user_id = str(settings.get("telegram_user_id", ""))
    
    # Se il token/user sono uguali e il bridge gira, non fare nulla
    if existing_bridge and existing_bridge.token == token and str(existing_bridge.authorized_user_id) == user_id:
        return existing_bridge

    # Altrimenti, ferma il vecchio se presente
    if existing_bridge:
        existing_bridge.stop()
    
    if not token:
        print("🤖 [Telegram] Bot Token non configurato. Salto avvio Link.")
        return None
        
    try:
        new_bridge = TelegramSovereignLink(orchestrator, token, user_id)
        t = threading.Thread(target=new_bridge.run, daemon=True, name="TelegramBotThread")
        t.start()
        return new_bridge
    except Exception as e:
        print(f"❌ [Telegram] Errore fatale all'avvio: {e}")
        return None
