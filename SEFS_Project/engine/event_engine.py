import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.config import ROOT_FOLDER, SUPPORTED_TYPES
from core.db_api import (
    register_or_update_file,
    save_file_embedding,
    delete_file_record
)

from engine.content_engine import extract_text
from engine.semantic_engine import generate_embedding
from engine.clustering_engine import assign_cluster
from engine.system_controller import rebuild_semantic_system


# ---------------- FILE TYPE FILTER ----------------

def is_supported_file(path):
    _, ext = os.path.splitext(path)
    return ext.lower() in SUPPORTED_TYPES


# ---------------- FILE SAFETY ----------------

def wait_for_file_ready(path, retries=5, delay=0.5):
    """
    Prevent reading file while OS is still writing it.
    """
    for _ in range(retries):
        try:
            with open(path, "rb"):
                return True
        except PermissionError:
            time.sleep(delay)
    return False


# ---------------- FILE PROCESSING ----------------

def process_file(path):
    """
    Full semantic processing pipeline.
    """

    if not wait_for_file_ready(path):
        print("→ File not ready")
        return

    print(f"→ Extracting content: {path}")
    text = extract_text(path)

    if not text:
        print("→ No readable content")
        return

    print("→ Generating embedding...")
    embedding = generate_embedding(text)

    if embedding is None:
        print("→ Embedding failed")
        return

    print("→ Registering file...")
    file_id = register_or_update_file(path)

    print("→ Assigning cluster...")
    cluster_id = assign_cluster(embedding)

    print(f"→ Assigned cluster: {cluster_id}")

    save_file_embedding(path, embedding, cluster_id)

    print("→ Metadata stored")

    # ⭐ Rebuild full semantic system
    rebuild_semantic_system()


def remove_file_record(path):
    delete_file_record(path)
    print("→ Metadata removed")

    rebuild_semantic_system()


def update_file_path(old_path, new_path):
    """
    Rename = delete old + process new
    """
    delete_file_record(old_path)
    process_file(new_path)


# ---------------- WATCHDOG HANDLER ----------------

class SEFSEventHandler(FileSystemEventHandler):

    def on_created(self, event):
        if not event.is_directory and is_supported_file(event.src_path):
            print(f"[CREATED] {event.src_path}")
            process_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and is_supported_file(event.src_path):
            print(f"[MODIFIED] {event.src_path}")
            process_file(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"[DELETED] {event.src_path}")
            remove_file_record(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            print(f"[RENAMED] {event.src_path} → {event.dest_path}")
            update_file_path(event.src_path, event.dest_path)


# ---------------- START MONITORING ----------------

def start_event_engine():
    event_handler = SEFSEventHandler()
    observer = Observer()
    observer.schedule(event_handler, ROOT_FOLDER, recursive=True)

    observer.start()
    print("🧠 SEFS monitoring:", ROOT_FOLDER)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


# ---------------- BOOTSTRAP ----------------

def bootstrap_existing_files():
    """
    Scan all existing files once at startup.
    """

    print("📂 Scanning existing files...")

    for root, dirs, files in os.walk(ROOT_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)

            if not is_supported_file(file_path):
                continue

            print(f"[BOOTSTRAP] {file_path}")
            process_file(file_path)

    print("✅ Initial scan complete")
