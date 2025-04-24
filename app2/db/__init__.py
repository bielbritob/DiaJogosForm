import sqlite3

def init_db(db_path: str = "data.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        version INTEGER DEFAULT 1,
        modality TEXT NOT NULL,
        wants_lunch INTEGER NOT NULL,
        total REAL NOT NULL,
        paid REAL NOT NULL DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(name, version))""")

    c.execute("""CREATE TABLE IF NOT EXISTS payment_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registration_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status INTEGER DEFAULT 0,
        payload_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(registration_id) REFERENCES registrations(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS registration_changes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registration_id INTEGER NOT NULL,
        old_value TEXT NOT NULL,
        new_value TEXT NOT NULL,
        changed_by TEXT DEFAULT 'system',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(registration_id) REFERENCES registrations(id))""")

    conn.commit()
    conn.close()