import qrcode
from io import BytesIO
import streamlit as st


def show_qr_code(payload):
    # Criar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    # Criar imagem e converter para bytes
    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def show_qr_code_old(payload: str):
    img = qrcode.make(payload)
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="QR Code para Pagamento")