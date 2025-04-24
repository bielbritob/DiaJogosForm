import sqlite3
import hashlib

def create_registration(name: str, modality: str, wants_lunch: bool, total: float):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    try:
        c.execute("UPDATE registrations SET is_active = 0 WHERE name = ?", (name,))
        c.execute("""INSERT INTO registrations (name, modality, wants_lunch, total)
                     VALUES (?, ?, ?, ?)""", (name, modality, int(wants_lunch), total))
        reg_id = c.lastrowid

        c.execute("""INSERT INTO registration_changes
                     (registration_id, old_value, new_value)
                     VALUES (?, ?, ?)""", (reg_id, '{}', f'Created v{reg_id}'))

        conn.commit()
        return reg_id
    finally:
        conn.close()

def get_active_registration(name: str):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("""SELECT * FROM registrations 
                 WHERE name = ? AND is_active = 1 
                 ORDER BY version DESC LIMIT 1""", (name,))
    row = c.fetchone()
    conn.close()

    if row:
        return {
            'id': row[0],
            'name': row[1],
            'version': row[2],
            'modality': row[3],
            'wants_lunch': bool(row[4]),
            'total': row[5],
            'paid': row[6],
            'created_at': row[8],
            'updated_at': row[9]
        }
    return None

def log_payment_attempt(reg_id: int, amount: float, payload: str):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    payload_hash = hashlib.sha256(payload.encode()).hexdigest()

    c.execute("""INSERT INTO payment_logs (registration_id, amount, payload_hash)
                 VALUES (?, ?, ?)""", (reg_id, amount, payload_hash))
    conn.commit()
    conn.close()