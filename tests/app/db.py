import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            modality TEXT NOT NULL,
            wants_lunch INTEGER NOT NULL,
            total REAL NOT NULL,
            paid INTEGER NOT NULL DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_registration(name, modality, wants_lunch, total):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO registrations (name, modality, wants_lunch, total)
        VALUES (?, ?, ?, ?)
    """, (name, modality, int(wants_lunch), total))
    conn.commit()
    conn.close()

def get_registration(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, modality, wants_lunch, total, paid FROM registrations WHERE name = ?", (name,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "modality": row[2],
            "wants_lunch": bool(row[3]),
            "total": row[4],
            "paid": bool(row[5])
        }
    return None

def update_payment_status(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE registrations SET paid = 1 WHERE name = ?", (name,))
    conn.commit()
    conn.close()
