# db/database.py

import sqlite3

DB_PATH = "watchdog.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            target_price REAL,
            last_known_price REAL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT,
            last_checked_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price REAL,
            checked_at TEXT,
            snapshot_path TEXT,
            source_url TEXT,
            raw_text TEXT
        )
    """)

    conn.commit()
    conn.close()