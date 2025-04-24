import streamlit as st
import sqlite3
import qrcode
from io import BytesIO
from datetime import datetime


# --------- DB FUNCTIONS -----------
def init_db(db_path: str = "data.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT    UNIQUE NOT NULL,
            modality     TEXT    NOT NULL,
            wants_lunch  INTEGER NOT NULL,
            total        REAL    NOT NULL,
            paid         INTEGER NOT NULL DEFAULT 0,
            timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_registration(name: str, modality: str, wants_lunch: bool, total: float, db_path: str = "data.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO registrations (name, modality, wants_lunch, total)
        VALUES (?, ?, ?, ?)
        """,
        (name, modality, int(wants_lunch), total)
    )
    conn.commit()
    conn.close()


def update_registration(name: str, modality: str, wants_lunch: bool, total: float,  db_path: str = "data.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """
        UPDATE registrations 
        SET modality = ?, wants_lunch = ?, total = ?
        WHERE name = ?
        """,
        (modality, int(wants_lunch), total, name))
    conn.commit()
    conn.close()


def get_registration(name: str, db_path: str = "data.db") -> dict:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "SELECT id, name, modality, wants_lunch, total, paid"
        " FROM registrations WHERE name = ?",
        (name,)
    )
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


def update_payment_status(name: str, db_path: str = "data.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE registrations SET paid = 1 WHERE name = ?", (name,))
    conn.commit()
    conn.close()


# --------- PIX CONFIG & GENERATOR -----------
PIX_KEY = "+556993707837"
MERCHANT_NAME = "Gabriella Brito Bernardo"
MERCHANT_CITY = "Porto Velho"


def generate_pix_payload(amount: float) -> str:
    def tlv(id_: str, value: str) -> str:
        return f"{id_}{len(value):02d}{value}"

    payload = tlv("00", "01")
    mai = tlv("00", "br.gov.bcb.pix") + tlv("01", PIX_KEY)
    payload += tlv("26", mai)
    payload += tlv("52", "0000")
    payload += tlv("53", "986")
    payload += tlv("54", f"{amount:.2f}")
    payload += tlv("58", "BR")
    payload += tlv("59", MERCHANT_NAME[:25])
    payload += tlv("60", MERCHANT_CITY[:15])

    txid = "INSC" + str(int(datetime.now().timestamp()))[-10:]
    payload += tlv("62", tlv("05", txid))

    def crc16(s: str) -> str:
        crc = 0xFFFF
        for char in s.encode('utf-8'):
            crc ^= char << 8
            for _ in range(8):
                crc = (crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1
                crc &= 0xFFFF
        return f"{crc:04X}"

    payload += "6304" + crc16(payload)
    return payload


def show_payment_page(name: str):
    registration = get_registration(name)
    if not registration:
        st.error("Registro não encontrado")
        return

    # Novo container para edição
    with st.container(border=True):
        st.subheader("Editar Inscrição")

        # Carrega dados atuais
        current_mods = registration['modality'].split(',')
        current_lunch = registration['wants_lunch']

        # Widgets para edição
        new_mods = st.multiselect(
            "Adicionar/Remover Modalidades",
            modalidades,
            default=current_mods,
            key=f"mods_{name}"
        )

        new_lunch = st.checkbox(
            "Adicionar Marmita",
            value=current_lunch,
            key=f"lunch_{name}"
        )

        # Calcula novo total
        new_total = len(new_mods) * price_modality
        if new_lunch:
            new_total += price_marmita

        # Exibe diferença de valores
        if new_total != registration['total']:
            diff = new_total - registration['total']
            st.write(f"**Diferença no valor:** {'+' if diff > 0 else ''}{diff:.2f}")
            st.write(f"**Novo total:** R$ {new_total:.2f}")

        # Botão para aplicar mudanças
        if st.button("Atualizar Inscrição", type="secondary"):
            update_registration(
                name,
                ",".join(new_mods),
                new_lunch,
                new_total
            )
            st.success("Inscrição atualizada! Atualize o QR Code abaixo.")
            st.rerun()


    st.header("Pagamento via PIX")

    # Resumo detalhado
    with st.expander("📝 Detalhes da Inscrição", expanded=True):

        st.subheader("**Resumo da Compra:**")
        st.write("")
        modalities = registration['modality'].split(',')
        st.write("**Modalidades:**")
        for mod in modalities:
            st.write(f"-- {mod} (R$ 5.00)")

        if registration['wants_lunch']:
            st.write(f"-- Marmita (R$ 20.00)")

        st.write(f"****Total:**** R$ {registration['total']:.2f}")
        st.write(f"**Status do pagamento:** {'✅ Pago' if registration['paid'] else '❌ Pendente'}")
        st.write(registration)
    # Gerar QR Code
    payload = generate_pix_payload(registration['total'])
    img = qrcode.make(payload)
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="QR Code para Pagamento")
    st.write(f"**Chave PIX:** `{PIX_KEY}`")

    if st.button("Marcar como Pago"):
        update_payment_status(name)
        st.success("Status atualizado! Obrigado pela confirmação.")
        st.rerun()


# --------- APP CONFIG -----------
st.set_page_config(page_title="Inscrição Dia de Jogos ADV", layout="centered")
init_db()

modalidades = ["Vôlei", "Futsal", "Tênis de mesa", "Pebolim"]
price_modality = 5.0
price_marmita = 20.0

if "step" not in st.session_state:
    st.session_state.step = "form"

if st.session_state.step == "form":
    st.title("Formulário de Inscrição")

    with st.form("inscricao", border=True):
        name = st.text_input("Nome completo").strip()
        existing = get_registration(name) if name else None

        # Pré-preencher se existir
        if existing:
            default_mods = existing['modality'].split(',')
            default_lunch = existing['wants_lunch']
        else:
            default_mods = []
            default_lunch = False

        modalities = st.multiselect(
            "Modalidades (R$ 5,00 cada)",
            modalidades,
            default=default_mods
        )

        wants_lunch = st.checkbox(
            "Adicionar marmita (R$ 20,00)",
            value=default_lunch
        )

        if st.form_submit_button("Enviar"):
            if not name:
                st.error("Por favor, insira seu nome completo")
            elif not modalities:
                st.error("Selecione pelo menos uma modalidade")
            else:
                total = len(modalities) * price_modality
                if wants_lunch:
                    total += price_marmita

                if existing:
                    update_registration(
                        name,
                        ",".join(modalities),
                        wants_lunch,
                        total
                    )
                    st.success("Inscrição atualizada!")
                else:
                    add_registration(
                        name,
                        ",".join(modalities),
                        wants_lunch,
                        total
                    )
                    st.success("Inscrição registrada!")

                st.session_state.step = "payment"
                st.session_state.name = name
                st.rerun()

elif st.session_state.step == "payment":
    show_payment_page(st.session_state.name)
    if st.button("Voltar ao Formulário"):
        st.session_state.step = "form"
        st.rerun()