import streamlit as st
import sqlite3
import qrcode
from io import BytesIO

#--------- Def's -----------

# ------- 2) Init  db -------
def init_db(db_path: str = "data.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            modality   TEXT    NOT NULL,
            wants_lunch TEXT NOT NULL,
            total     TEXT    NOT NULL,
            timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_registration(name:str, modality:str, wants_lunch:bool, total:int,
                     db_path: str = "data.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "INSERT INTO registrations (name, modality, wants_lunch, total) VALUES (?, ?, ?, ?)",
        (name,
         modality,
         wants_lunch,
         total)
    )
    conn.commit()
    conn.close()

# ------- 3) GERAR PAYLOAD Pix (EMVCo) -------
def generate_pix_payload(amount: float) -> str:
    # implementação simples baseada no formato oficial EMVCo para Pix
    from datetime import datetime
    # Monta manualmente os campos (você pode usar libs como 'pixqrcode' para facilitar)
    def tlv(id_: str, value: str) -> str:
        return f"{id_}{len(value):02d}{value}"

    payload = ""
    # 00: Payload Format Indicator
    payload += tlv("00", "01")
    # 26: Merchant Account Information
    mai  = tlv("00", "br.gov.bcb.pix")
    mai += tlv("01", PIX_KEY)
    payload += tlv("26", mai)
    # 52: Merchant Category Code
    payload += tlv("52", "0000")
    # 53: Currency (986 = BRL)
    payload += tlv("53", "986")
    # 54: Amount
    payload += tlv("54", f"{amount:.2f}")
    # 58: Country
    payload += tlv("58", "BR")
    # 59: Merchant Name
    payload += tlv("59", MERCHANT_NAME[:25])
    # 60: Merchant City
    payload += tlv("60", MERCHANT_CITY[:15])
    # 62: Additional Data Field Template (ex: descrição, id do tx)
    add = tlv("05", f"{PIX_DESCRIPTION} {datetime.now().strftime('%Y%m%d%H%M%S')}")
    payload += tlv("62", add)
    # 63: CRC16
    def crc16(s: bytes) -> str:
        poly = 0x1021
        reg  = 0xFFFF
        for b in s:
            reg ^= b << 8
            for _ in range(8):
                reg = (reg << 1) ^ poly if (reg & 0x8000) else reg << 1
                reg &= 0xFFFF
        return f"{reg:04X}"
    payload += "6304" + crc16(payload.encode("utf-8"))
    return payload

# ------- 4) PAGAMENTO (QR + chave) -------
def show_payment_page(amount: float):
    st.header("Pagamento via Pix")
    st.write(f"💰 **Valor a pagar:** R$ {amount:.2f}")
    payload = generate_pix_payload(amount)
    # gera QR code
    img = qrcode.make(payload)
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="Aponte sua câmera para o QR code", use_column_width=False)
    st.write("🔑 **Chave Pix:**", PIX_KEY)




#-------- 1) Configs -------------
modalidades = ["Vôlei", "Futsal", "Tênis de mesa", "Pebolim"]
precos = 5

# ------- Configs PIX -------
PIX_KEY         = "69993707837"      # sua chave Pix
MERCHANT_NAME   = "Terceirinhos"
MERCHANT_CITY   = "Porto Velho"
PIX_DESCRIPTION = "Inscrição Dia de Jogos ADV"

# ------- Conf Page -------
st.set_page_config(page_title="Form Inscrição Dia de Jogos ADV Terceirinhos!", layout="centered", page_icon="🏐")
init_db()

#-------- Estados ------
if "step" not in st.session_state:
    st.session_state.step = "form"

if st.session_state.step == "form":
    st.title("Formulário de Inscrição")
    with st.form("inscricao"):
        name = st.text_input("Nome completo", )

        st.badge("(Cada modalidade é R$5,00)", color="orange")
        modality = st.pills("Modalidades:", options=modalidades,selection_mode="multi")
        #modality    = st.selectbox("Modalidade", list(PRICES.keys()))
        st.write("Escolha as modalidades:")
        #modality = st.checkbox("Futsal",  )
        st.write(f"Você escolheu : {modality}")
        st.divider()
        wants_lunch = st.checkbox("Deseja almoço?")

        submit_btn = st.form_submit_button("Enviar")

    if submit_btn:
        if not name:
            st.error("Por favor, preencha seu nome.")
        # implementar aq a verificação de nome no db
        else:
            total = precos*modality
            print(total)
            add_registration(name, modality, wants_lunch, total=total)
            st.success(f"Inscrição gravada! Agora prossiga para o pagamento.")
            st.session_state.amount = total
            st.session_state.step   = "payment"
            st.rerun()

elif st.session_state.step == "payment":
    show_payment_page(st.session_state.amount)
#------------ Fim estados -------------------