import streamlit as st
from config import PIX_KEY, DEBUG, PRICE_PER_MODALITY
from db import get_registration, add_registration, update_payment_status
from pix import generate_pix_payload, generate_qrcode

def show_payment_page(name, amount):
    st.header("Pagamento via Pix")
    st.write(f"💰 **Valor a pagar:** R$ {amount:.2f}")
    payload = generate_pix_payload(amount)
    qr = generate_qrcode(payload)
    st.image(qr.getvalue(), caption="Aponte sua câmera para o QR code")
    st.write("🔑 **Chave Pix:**", PIX_KEY)

    if DEBUG:
        st.code(payload)

    if st.button("Já realizei o pagamento"):
        update_payment_status(name)
        st.success("Pagamento confirmado! Obrigado.")

def show_form():
    st.title("Formulário de Inscrição")
    modalidades = ["Vôlei", "Futsal", "Tênis de mesa", "Pebolim"]
    with st.form("inscricao", border=True):
        name = st.text_input("Nome completo")
        st.badge("Cada modalidade custa R$ 5,00", color="orange")
        selecionadas = st.pills("Modalidades", modalidades, selection_mode="multi")
        wants_lunch = st.checkbox("Deseja almoço?")
        submit_btn = st.form_submit_button("Enviar")

        if submit_btn:
            existing = get_registration(name)
            if not name:
                st.error("Por favor, preencha seu nome.")
            elif len(selecionadas) < 1:
                st.error("Por favor, selecione alguma modalidade.")
            else:
                total = len(selecionadas) * PRICE_PER_MODALITY
                if existing:
                    if not existing['paid']:
                        st.info("Você já se registrou, mas o pagamento está pendente.")
                        st.session_state.name = name
                        st.session_state.amount = existing['total']
                        st.session_state.step = "payment"
                        st.rerun()
                    else:
                        st.success("Você já se registrou e o pagamento foi confirmado!")
                else:
                    add_registration(name, ",".join(selecionadas), wants_lunch, total)
                    st.success("Inscrição gravada! Agora prossiga para o pagamento.")
                    st.session_state.name = name
                    st.session_state.amount = total
                    st.session_state.step = "payment"
                    st.rerun()
