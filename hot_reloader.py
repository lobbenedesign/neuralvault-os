import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from vault_sdk import NeuralVaultClient

class HotReloaderHandler(FileSystemEventHandler):
    def __init__(self, client, root_path):
        self.client = client
        self.root_path = root_path

    def on_modified(self, event):
        if event.is_directory:
            return
        
        filename = event.src_path
        if not filename.endswith('.py'):
            return
            
        print(f"🔥 [Hot-Reloader] Detected change in: {os.path.relpath(filename, self.root_path)}")
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if content:
                # Trigger incremental re-ingestion via NeuralVault API
                # This will automatically hit the ASTExtractor thanks to Sprint 2 logic
                res = self.client.synapse_text(content, {
                    "source": os.path.basename(filename),
                    "file_type": "py",
                    "namespace": "hot_reloader",
                    "path": os.path.relpath(filename, self.root_path)
                })
                print(f"✅ [Hot-Reloader] Synapsed AST for {os.path.basename(filename)}. ID: {res.get('id')}")
                
        except Exception as e:
            print(f"❌ [Hot-Reloader] Error processing {filename}: {e}")

if __name__ == "__main__":
    # Watch the current directory (project root) but skip venv/node_modules/etc.
    WATCH_PATH = "."
    client = NeuralVaultClient()
    
    event_handler = HotReloaderHandler(client, os.path.abspath(WATCH_PATH))
    observer = Observer()
    
    # We schedule on specific subdirectories to avoid watching venv and .git
    for folder in ["core", "retrieval", "agents", "dashboard", "api"]:
        if os.path.exists(folder):
            observer.schedule(event_handler, folder, recursive=True)
            print(f"🛰️ [Hot-Reloader] Watching directory: {folder}/")
            
    if not observer.emitters:
        print("⚠️ [Hot-Reloader] No target directories found. Watching current directory (non-recursive).")
        observer.schedule(event_handler, WATCH_PATH, recursive=False)
    
    print("🔥 Graphify-style Hot-Reloader active. Saving a .py file will trigger re-ingestion.")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
