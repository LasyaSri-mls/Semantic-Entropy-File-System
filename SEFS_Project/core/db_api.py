import hashlib
import time
import pickle
import sqlite3
from core.config import DATABASE_PATH


# ---------------- CONNECTION ----------------

def get_connection():
    return sqlite3.connect(DATABASE_PATH)


# ---------------- INITIALIZE DATABASE ----------------

def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    # FILE METADATA
    cur.execute("""
    CREATE TABLE IF NOT EXISTS FILES (
        file_id TEXT PRIMARY KEY,
        path TEXT UNIQUE,
        name TEXT,
        type TEXT,
        content_hash TEXT,
        created_at REAL,
        last_modified REAL,
        status TEXT
    )
    """)

    # SEMANTIC DATA
    cur.execute("""
    CREATE TABLE IF NOT EXISTS SEMANTICS (
        file_id TEXT PRIMARY KEY,
        embedding BLOB,
        updated_at REAL,
        FOREIGN KEY(file_id) REFERENCES FILES(file_id)
    )
    """)

    # CLUSTERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS CLUSTERS (
        cluster_id TEXT PRIMARY KEY,
        label TEXT,
        centroid BLOB,
        created_at REAL
    )
    """)

    # FILE ↔ CLUSTER RELATION
    cur.execute("""
    CREATE TABLE IF NOT EXISTS FILE_CLUSTER_MAP (
        file_id TEXT PRIMARY KEY,
        cluster_id TEXT,
        confidence REAL,
        FOREIGN KEY(file_id) REFERENCES FILES(file_id),
        FOREIGN KEY(cluster_id) REFERENCES CLUSTERS(cluster_id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


# ---------------- FILE IDENTITY ----------------

def generate_file_id(file_path):
    return hashlib.md5(file_path.encode()).hexdigest()


def compute_file_hash(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None


# ---------------- FILE REGISTRATION ----------------

def register_or_update_file(file_path):
    file_id = generate_file_id(file_path)
    file_hash = compute_file_hash(file_path)
    timestamp = time.time()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO FILES
    (file_id, path, name, type, content_hash, created_at, last_modified, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
    """, (
        file_id,
        file_path,
        file_path.split("\\")[-1],
        file_path.split(".")[-1],
        file_hash,
        timestamp,
        timestamp
    ))

    conn.commit()
    conn.close()
    return file_id


# ---------------- DELETE ----------------

def delete_file_record(file_path):
    file_id = generate_file_id(file_path)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM FILES WHERE file_id=?", (file_id,))
    cur.execute("DELETE FROM SEMANTICS WHERE file_id=?", (file_id,))
    cur.execute("DELETE FROM FILE_CLUSTER_MAP WHERE file_id=?", (file_id,))

    conn.commit()
    conn.close()


# ---------------- SEMANTIC STORAGE ----------------

def store_semantic_data(file_id, embedding):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO SEMANTICS
    (file_id, embedding, updated_at)
    VALUES (?, ?, ?)
    """, (
        file_id,
        pickle.dumps(embedding),
        time.time()
    ))

    conn.commit()
    conn.close()


def save_file_embedding(path, embedding, cluster_id):
    file_id = register_or_update_file(path)
    store_semantic_data(file_id, embedding)
    assign_file_to_cluster(file_id, cluster_id)


# ---------------- CLUSTER MANAGEMENT ----------------

def store_cluster(cluster_id, label, centroid=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO CLUSTERS
    (cluster_id, label, centroid, created_at)
    VALUES (?, ?, ?, ?)
    """, (
        cluster_id,
        label,
        pickle.dumps(centroid) if centroid is not None else None,
        time.time()
    ))

    conn.commit()
    conn.close()


def assign_file_to_cluster(file_id, cluster_id, confidence=1.0):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO FILE_CLUSTER_MAP
    (file_id, cluster_id, confidence)
    VALUES (?, ?, ?)
    """, (file_id, cluster_id, confidence))

    conn.commit()
    conn.close()


# ---------------- FETCH EMBEDDINGS ----------------

def get_all_embeddings():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT f.file_id, f.path, s.embedding
    FROM FILES f
    JOIN SEMANTICS s ON f.file_id = s.file_id
    """)

    rows = cur.fetchall()
    conn.close()

    results = []
    for file_id, path, emb_blob in rows:
        results.append({
            "file_id": file_id,
            "path": path,
            "embedding": pickle.loads(emb_blob)
        })

    return results


# ---------------- QUERY HELPERS ----------------

def get_files_in_cluster(cluster_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT f.path
    FROM FILES f
    JOIN FILE_CLUSTER_MAP m ON f.file_id = m.file_id
    WHERE m.cluster_id=?
    """, (cluster_id,))

    results = [row[0] for row in cur.fetchall()]
    conn.close()
    return results


def get_file_path_by_id(file_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT path FROM FILES WHERE file_id=?", (file_id,))
    row = cur.fetchone()
    conn.close()

    return row[0] if row else None


# ---------------- DEBUG ----------------

def debug_show_files():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT file_id, name, path, status FROM FILES")
    print("FILES table:", cur.fetchall())
    conn.close()
