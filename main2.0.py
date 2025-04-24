import pandas as pd
import streamlit as st
import sqlite3
import qrcode
from io import BytesIO
from datetime import datetime
import hashlib
import client.Secret as secret

# --------- DB SCHEMA 2.0 -----------
def init_db(db_path: str = "data.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Tabela principal com versionamento
    c.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT NOT NULL,
            version      INTEGER DEFAULT 1,
            modality     TEXT NOT NULL,
            wants_lunch  INTEGER NOT NULL,
            total        REAL NOT NULL,
            paid         REAL NOT NULL DEFAULT 0,
            is_active    INTEGER DEFAULT 1,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, version)
        )
    """)

    # Histórico de pagamentos
    c.execute("""
        CREATE TABLE IF NOT EXISTS payment_logs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_id INTEGER NOT NULL,
            amount       REAL NOT NULL,
            status       INTEGER DEFAULT 0,
            payload_hash TEXT NOT NULL,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(registration_id) REFERENCES registrations(id)
        )
    """)

    # Log de alterações
    c.execute("""
        CREATE TABLE IF NOT EXISTS registration_changes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_id INTEGER NOT NULL,
            old_value    TEXT NOT NULL,
            new_value    TEXT NOT NULL,
            changed_by   TEXT DEFAULT 'system',
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(registration_id) REFERENCES registrations(id)
        )
    """)

    conn.commit()
    conn.close()


# --------- DB OPERATIONS 2.0 -----------
def create_registration(name: str, modality: str, wants_lunch: bool, total: float):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    try:
        # Inativa versões anteriores
        c.execute("""
            UPDATE registrations 
            SET is_active = 0 
            WHERE name = ?
        """, (name,))

        # Cria nova versão
        c.execute("""
            INSERT INTO registrations 
            (name, modality, wants_lunch, total)
            VALUES (?, ?, ?, ?)
        """, (name, modality, int(wants_lunch), total))

        reg_id = c.lastrowid

        # Log da criação
        c.execute("""
            INSERT INTO registration_changes
            (registration_id, old_value, new_value)
            VALUES (?, ?, ?)
        """, (reg_id, '{}', f'Created v{reg_id}'))

        conn.commit()
        return reg_id

    finally:
        conn.close()


def log_payment_attempt(reg_id: int, amount: float, payload: str):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    payload_hash = hashlib.sha256(payload.encode()).hexdigest()

    c.execute("""
        INSERT INTO payment_logs
        (registration_id, amount, payload_hash)
        VALUES (?, ?, ?)
    """, (reg_id, amount, payload_hash))

    conn.commit()
    conn.close()


def get_active_registration(name: str):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("""
        SELECT * FROM registrations 
        WHERE name = ? AND is_active = 1
        ORDER BY version DESC
        LIMIT 1
    """, (name,))

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


# --------- PIX GENERATOR 2.0 -----------
def generate_pix_payload(reg_id: int, version: int, amount: float):
    def tlv(id_: str, value: str):
        return f"{id_}{len(value):02d}{value}"

    # TXID único e rastreável
    txid = f"ADV{reg_id:04d}-V{version}-{int(datetime.now().timestamp())}"

    payload = ''.join([
        tlv("00", "01"),
        tlv("26", tlv("00", "br.gov.bcb.pix") + tlv("01", secret.PIX_KEY)),
        tlv("52", "0000"),
        tlv("53", "986"),
        tlv("54", f"{amount:.2f}"),
        tlv("58", "BR"),
        tlv("59", secret.MERCHANT_NAME[:25]),
        tlv("60", secret.MERCHANT_CITY[:15]),
        tlv("62", tlv("05", txid))
    ])

    # CRC otimizado
    crc = 0xFFFF
    for b in payload.encode('utf-8'):
        crc ^= b << 8
        for _ in range(8):
            crc = (crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1
            crc &= 0xFFFF

    return payload + f"6304{crc:04X}"


# --------- UI COMPONENTS 2.0 -----------
def registration_summary(reg):
    st.subheader("📋 Resumo da Inscrição")

    cols = st.columns([1, 2])
    with cols[0]:
        st.metric("Total a Pagar", f"R$ {reg['total']}")
        if str(reg['paid']) >= str(reg['total']):
            st.metric("Status", "✅ Pago")
        else:
            st.metric("Status",  "❌ Pendente")

        #st.metric("Status", "✅ Pago" if reg['paid'] >= reg['total'] else "❌ Pendente")

    with cols[1]:
        st.write("**Modalidades:**")
        for mod in reg['modality'].split(','):
            st.write(f"- {mod} (R$ 5.00)")

        if reg['wants_lunch']:
            st.write("- 🍱 Marmita (R$ 20.00)")

    st.caption(f"Última atualização: {reg['updated_at']}")


def payment_history(reg_id):
    conn = sqlite3.connect("data.db")
    df = pd.read_sql("""
        SELECT created_at, amount, payload_hash 
        FROM payment_logs
        WHERE registration_id = ?
        ORDER BY created_at DESC
    """, conn, params=(reg_id,))

    if not df.empty:
        st.subheader("📜 Histórico de Pagamentos")
        st.dataframe(df.style.format({'amount': 'R$ {:.2f}'}), use_container_width=True)
    conn.close()


# --------- APP FLOW 2.0 -----------
def main():
    st.set_page_config("Inscrições ADV 2.0", "🏐", "centered")
    init_db()

    if 'reg_data' not in st.session_state:
        st.session_state.reg_data = None

    # Página principal
    if not st.session_state.reg_data:
        with st.form("main_form"):
            name = st.text_input("Nome Completo").strip()

            if st.form_submit_button("Carregar Inscrição"):
                reg = get_active_registration(name)
                if reg:
                    st.session_state.reg_data = reg
                    st.rerun()

    # Página de gestão
    else:
        reg = st.session_state.reg_data
        tab_pay, tab_edit = st.tabs(["Pagamento", "Editar Inscrição"])

        with tab_pay:
            registration_summary(reg)

            # Gerar QR Code dinâmico
            payload = generate_pix_payload(reg['id'], reg['version'], reg['total'])
            log_payment_attempt(reg['id'], reg['total'], payload)

            #img = qrcode.make(payload)
            #st.image(BytesIO(img.save(BytesIO(),format="PNG")), caption="Escaneie para pagar")

            img = qrcode.make(payload)
            buf = BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue(), caption="QR Code para Pagamento")

            if st.button("Confirmar Pagamento", type="primary"):
                # Lógica de confirmação de pagamento
                pass

        with tab_edit:
            # Interface de edição inteligente
            pass

        payment_history(reg['id'])

        if st.button("Voltar"):
            st.session_state.reg_data = None
            st.rerun()


if __name__ == "__main__":
    main()