document.getElementById('sendBtn').addEventListener('click', async () => {
  const status = document.getElementById('status');
  status.innerText = "Recupero contenuto...";

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Esegue uno script nella pagina per recuperare il testo principale
    const [{ result }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => document.body.innerText.substring(0, 50000)
    });

    status.innerText = "Invio alla Nebula...";

    const response = await fetch('http://localhost:8001/api/ingest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: result,
        metadata: {
          source: tab.url,
          title: tab.title,
          agent: "Aura_Bridge_Extension"
        }
      })
    });

    if (response.ok) {
      status.style.color = "#4ade80";
      status.innerText = "✅ Nodo archiviato con successo!";
    } else {
      throw new Error("Errore API");
    }
  } catch (err) {
    status.style.color = "#ef4444";
    status.innerText = "❌ Fallito: Assicurati che api.py sia attivo.";
    console.error(err);
  }
});
