import sqlite3
from core.config import DATABASE_PATH


def get_connection():
    """
    Creates and returns a database connection.
    Ensures database file exists.
    """
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # FILES TABLE
    cursor.execute("""
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

    # SEMANTICS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SEMANTICS (
        file_id TEXT PRIMARY KEY,
        embedding BLOB,
        cluster_id TEXT,
        keywords TEXT,
        summary TEXT,
        updated_at REAL
    )
    """)

    # CLUSTERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CLUSTERS (
        cluster_id TEXT PRIMARY KEY,
        label TEXT,
        centroid BLOB,
        created_at REAL
    )
    """)

    # FILE ↔ CLUSTER MAPPING
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS FILE_CLUSTER_MAP (
        file_id TEXT PRIMARY KEY,
        cluster_id TEXT,
        confidence REAL
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")
