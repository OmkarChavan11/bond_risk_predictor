import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# Import the function from your sibling script
from db_ingestion import insert_ocr_with_chunks

# Update this path to match your Windows directory structure
WATCH_DIR = os.path.abspath("../../data/ocr_output/varthana")

class OCRHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Only process text files, ignore directories
        if not event.is_directory and event.src_path.endswith(".txt"):
            filename = os.path.basename(event.src_path)
            print(f"🆕 New OCR file detected: {filename}")
            
            # Brief pause to ensure the file is fully written to disk
            time.sleep(1) 
            
            # Determine DocType from filename (e.g., 'Varthana_Q3.txt' -> 'Quarterly')
            doc_type = "Quarterly_Report" if "Q" in filename.upper() else "IM"
            
            insert_ocr_with_chunks(
                file_path=event.src_path,
                issuer_name="Varthana",
                doc_type=doc_type
            )
            print(f"✅ Ingestion complete for {filename}")

if __name__ == "__main__":
    if not os.path.exists(WATCH_DIR):
        os.makedirs(WATCH_DIR)
        print(f"Created directory: {WATCH_DIR}")

    event_handler = OCRHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    
    print(f"👀 Watcher started. Monitoring: {WATCH_DIR}")
    print("Press Ctrl+C to stop.")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nWatcher stopped.")
    observer.join()