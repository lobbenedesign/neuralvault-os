#!/bin/bash
# 🏺 Opencode NeuralVault Initer (v1.0)
# Esegui questo script per attivare il collegamento con il Vault nel tuo workspace Opencode.

echo "📡 Inizializzazione NeuralVault Bridge per Opencode..."

# Percorso dello script bridge
BRIDGE_PATH="/Users/giuseppelobbene/Downloads/DATABASE VETTORIALE/integrations/nv-link.py"

# Creazione alias rapidi per il terminale di Opencode
alias nv="python3 '$BRIDGE_PATH'"
alias nv-query="python3 '$BRIDGE_PATH' query"
alias nv-save="python3 '$BRIDGE_PATH' ingest"

# Controllo salute della connessione
if curl -s -o /dev/null --connect-timeout 2 "http://127.0.0.1:8001/api/health"; then
    echo "✅ Connessione stabilita: NeuralVault è ONLINE."
    # Esempio di pre-fetch: carichiamo il contesto del progetto corrente
    CONTEXT=$(python3 "$BRIDGE_PATH" query "Progetto corrente: $(basename "$PWD")" | head -n 10)
    export NV_CURRENT_CONTEXT="$CONTEXT"
else
    echo "⚠️ Attenzione: NeuralVault API (api.py) non risponde sulla porta 8001."
    echo "👉 Avvia la dashboard per abilitare la memoria neurale."
fi

echo "🚀 Pronto! Usa 'nv-query' per cercare o 'nv-save' per archiviare."
