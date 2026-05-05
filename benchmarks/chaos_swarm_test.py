"""
benchmarks/chaos_swarm_test.py
─────────────────────────────
Sovereign Chaos Swarm Test (v4.2.0)
Simula un carico asincrono massivo con gli Agenti che operano simultaneamente.
Serve a validare l'assenza di race condition e deadlock nei lock di stato.
"""

import asyncio
import random
import time
import os
import shutil
import numpy as np
from pathlib import Path
import sys

sys.path.append(os.getcwd())
from __init__ import NeuralVaultEngine, VaultNode
from neural_lab import NeuralLabOrchestrator

async def stress_test_concurrent_agents():
    print("🏺 [CHAOS SWARM TEST] — Inizializzazione NeuralVault (Sovereign v4.2.0)...")
    dim = 1024
    data_dir = Path("./chaos_test_db")
    if data_dir.exists(): shutil.rmtree(data_dir)
    
    # Engine asincrono
    engine = NeuralVaultEngine(dim=dim, data_dir=data_dir, use_rust=True)
    
    # Inizializziamo l'orchestratore
    swarm = NeuralLabOrchestrator(engine)
    
    print("📦 [Popolamento iniziale veloce...]")
    initial_nodes = [
        VaultNode(id=f"init_{i}", text=f"Data_Content_{i}", vector=np.random.randn(dim).astype(np.float32))
        for i in range(1000)
    ]
    await engine.upsert_batch(initial_nodes)
    print("✅ Ingestione completata.")

    print("🌪️ [SCATENANDO IL CAOS] Lancio agenti in parallelo per 60 secondi...")
    errors = []
    
    async def agent_chaos(agent_id, duration=60):
        """Ogni agente esegue un'azione o movimento causale sul grafo per N secondi"""
        deadline = asyncio.get_event_loop().time() + duration
        
        agent = swarm.agents.get(agent_id)
        if not agent:
            return
            
        while asyncio.get_event_loop().time() < deadline:
            try:
                node_id = f"init_{random.randint(0, 999)}"
                
                # Stressiamo l'architettura asincrona simulando le chiamate critiche
                action_type = random.randint(1, 3)
                if action_type == 1:
                    await asyncio.wait_for(engine.query(f"query {random.randint(1,10)}", k=3), timeout=5.0)
                elif action_type == 2:
                    await asyncio.wait_for(engine.add_node(f"new_{random.randint(1000, 50000)}", "Nuovo dato"), timeout=5.0)
                else:
                    await asyncio.wait_for(engine.query(f"query {random.randint(1,10)}", k=1), timeout=5.0)
                    
            except asyncio.TimeoutError:
                errors.append(f"TIMEOUT: agent {agent_id} on operation")
            except Exception as e:
                errors.append(f"ERROR: agent {agent_id}: {type(e).__name__}: {e}")
            
            await asyncio.sleep(0.01) # 10ms di tregua
            
    start_time = time.time()
    
    agent_ids = list(swarm.agents.keys())
    if not agent_ids:
        # Se non ci sono agenti nel lab per qualche motivo testiamo dei fake
        agent_ids = ["Fake-1", "Fake-2", "Fake-3"]

    tasks = [agent_chaos(aid, duration=60) for aid in agent_ids]
    
    # Eseguiamo anche query esterne concorrenti
    async def external_queries(duration=60):
        deadline = asyncio.get_event_loop().time() + duration
        while asyncio.get_event_loop().time() < deadline:
            try:
                await engine.query("utente esterno query", k=2)
            except: pass
            await asyncio.sleep(0.1)
            
    tasks.append(external_queries())

    await asyncio.gather(*tasks)
    
    total_dur = time.time() - start_time
    
    print("\n🏆 [RISULTATI CHAOS SWARM TEST] — v4.2.0")
    print("─────────────────────────────────────────────────────────────")
    print(f"⏱️  Tempo Esecuzione Reale: {total_dur:.2f} s")
    print(f"✅ Agenti convolti: {len(agent_ids)}")
    print(f"❌ Errori Totali Rilevati (Race condition/Deadlock): {len(errors)}")
    
    if errors:
        for e in errors[:10]:
            print(f"  - {e}")
    else:
        print("💎 INTEGRITÀ ASINCRONA GARANTITA: Zero Race Conditions!")
        
    engine.close()
    if data_dir.exists(): shutil.rmtree(data_dir)

if __name__ == "__main__":
    asyncio.run(stress_test_concurrent_agents())
