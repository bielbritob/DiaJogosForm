import qrcode
from io import BytesIO
import streamlit as st

def show_qr_code(payload: str):
    img = qrcode.make(payload)
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="QR Code para Pagamento")