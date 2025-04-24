import streamlit as st

from db import init_db
from db.operations import create_registration
from db.operations import get_active_registration
from components import registration_summary, payment_history
from generator import generate_pix_payload
from qrcode_utils import show_qr_code
import config

def main():
    st.set_page_config("Inscrições ADV 2.0", "🏐", "centered")
    init_db()

    if config.Debug:
        st.write(st.session_state)

    if 'currentPage' not in st.session_state:
        st.session_state['currentPage'] = 'home'

    if 'reg_data' not in st.session_state:
        st.session_state['reg_data'] = None


    if st.session_state['currentPage'] == 'home':
        config.custom_title_home()

        config.nobt_background_home()

        with st.form("main_form"):
            name = st.text_input("Nome Completo").strip()

            if st.form_submit_button("Avançar"):
                if name != "":
                    reg = get_active_registration(name)
                    if reg:
                        st.session_state['reg_data'] = reg
                        st.session_state['currentPage'] = 'payment'
                        st.rerun()
                    else:
                        st.session_state['currentPage'] = 'register'
                        st.rerun()
                else:
                    st.error("digite um nome")

    elif st.session_state['currentPage'] == 'payment':
        reg = st.session_state['reg_data']
        tab_pay, tab_edit = st.tabs(["Pagamento", "Editar Inscrição"])

        with tab_pay:
            registration_summary(reg)
            payload = generate_pix_payload(reg['id'], reg['version'], reg['total'])

            from db.operations import log_payment_attempt
            log_payment_attempt(reg['id'], reg['total'], payload)

            show_qr_code(payload)

            if st.button("Confirmar Pagamento", type="primary"):
                pass

        with tab_edit:
            pass

        payment_history(reg['id'])

        if st.button("Voltar"):
            st.session_state['currentPage'] = 'home'
            st.session_state['reg_data'] = None
            st.rerun()

    elif st.session_state['currentPage'] == 'register':
        config.custom_title_register()
        st.divider()
        col1, col2, col3 = st.columns([1.5,0.000000000000001,1],  border=False, vertical_alignment= 'center')
        with col3:
            st.image(image=config.BANNER_HOME, use_container_width=True, width=10)

        with col1:
            with st.form("main_form"):
                name = st.text_input("Nome Completo").strip()

                selected_modalities = st.pills(f"Modalidades (R$ {int(config.price_modality)},00 cada)", config.modalidades, selection_mode='multi')
                wants_lunch = st.checkbox(
                    f"Adicionar marmita (R$ {int(config.price_marmita)},00)", value=False)

                total = 0
                if st.form_submit_button("Avançar"):
                    if not name:
                        st.error("Por favor, insira seu nome completo")
                    elif not config.modalidades:
                        st.error("Selecione ao menos uma modalidade")
                    else:
                        total = len(selected_modalities) * config.price_modality
                        if wants_lunch:
                            total += config.price_marmita

                    create_registration(name=name,modality=",".join(selected_modalities),wants_lunch=wants_lunch,total=total)

                if config.Debug:
                    st.write('total:', total)
        if config.Debug:
            if st.button("Voltar"):
                st.session_state['currentPage'] = 'home'
                st.rerun()


if __name__ == "__main__":
    main()