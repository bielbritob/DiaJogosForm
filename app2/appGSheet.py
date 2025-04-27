import streamlit as st

from components import registration_summary
from generator import generate_pix_payload
from qrcode_utils import show_qr_code
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import hashlib
import config
from datetime import datetime

def _get_conn():
    return st.connection("gsheets", type=GSheetsConnection)


def create_registration(name: str, modality: str, wants_lunch: bool, total: float):
    conn = _get_conn()

    # Desativa registros anteriores
    reg_df = conn.read(worksheet="registrations")
    if not reg_df.empty:
        mask = (reg_df["name"] == name) & (reg_df["is_active"] == 1)
        if not reg_df[mask].empty:
            updated_data = reg_df[mask].copy()
            updated_data["is_active"] = 0
            conn.update(worksheet="registrations", data=updated_data)

    # Cria novo registro
    new_id = str(datetime.now().timestamp())
    new_version = 1 if reg_df.empty else reg_df[reg_df["name"] == name]["version"].max() + 1

    new_reg = pd.DataFrame([{
        "name": name,
        "modality": modality,
        "wants_lunch": int(wants_lunch),
        "total": total,
        "paid": 0,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": new_version,
        "is_active": 1,
    }])

    conn.update(worksheet="registrations", data=new_reg)

    # Log de alteração
    changes_df = pd.DataFrame([{
        "registration_name": name,
        "old_value": f"{total}",
        "new_value": f"Created v{new_version}", #por logica pagou x falta y
        "changed_by": "system",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

    conn.update(worksheet="registrationsChanges", data=changes_df)

    return new_id

def get_active_registration(name: str):
    conn = _get_conn()

    try:
        # Query para pegar o registro mais recente ATIVO
        sql = f'''
            SELECT * 
            FROM "registrations" 
            WHERE 
                LOWER(name) = LOWER('{name}') AND 
                is_active = 1 
            ORDER BY version DESC 
            LIMIT 1
        '''

        df = conn.query(sql=sql, ttl=10)

        if not df.empty:
            # Mapeamento das colunas para o formato esperado
            row = df.iloc[0]
            return {
                'name': row['name'],
                'modality': row['modality'],  # Verifique o nome da coluna!
                'wants_lunch': bool(row['wants_lunch']),
                'total': row['total'],
                'paid': row['paid'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'version': row['version'],
            }

        # Verifica se o nome existe em qualquer registro
        df_all = conn.read(worksheet="registrations")
        if not df_all.empty and (df_all['name'].str.lower() == name.lower()).any():
            st.error("⚠️ Seu cadastro está inativo. Entre em contato para reativar.")
            return None  # Não retorna dados

        return None  # Nenhum registro encontrado

    except Exception as e:
        st.error(f"Erro na busca: {str(e)}")
        return None

def log_payment_attempt(amount: float, payload: str):
    conn = _get_conn()
    payload_hash = hashlib.sha256(payload.encode()).hexdigest()

    new_log = pd.DataFrame([{
        "amount": amount,
        "status": 0,
        "payload_hash": payload_hash,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

    conn.update(worksheet="paymentLogs", data=new_log)





def main():
    st.set_page_config("Inscrições ADV 2.0", "🏐", "centered")
    #init_db()

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
                    print(reg)
                    reg = get_active_registration(name)
                    if isinstance(reg, dict):  # Registro ativo encontrado
                        st.session_state['reg_data'] = reg
                        st.session_state['currentPage'] = 'payment'
                        st.rerun()
                    else:  # Novo registro
                        st.session_state['currentPage'] = 'register'
                        st.rerun()
                else:
                    st.error("Por favor, insira seu nome completo")

    elif st.session_state['currentPage'] == 'payment':
        reg = st.session_state['reg_data']
        tab_pay, tab_edit = st.tabs(["Pagamento", "Editar Inscrição"])

        with tab_pay:
            registration_summary(reg)
            payload = generate_pix_payload(reg['version'], reg['total'])
            log_payment_attempt(reg['total'], payload)

            show_qr_code(payload)

            if config.Debug:
                if st.button("Confirmar Pagamento", type="primary"):
                    pass

        with tab_edit:
            pass

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

                    reg_data = {
                'name': name,
                'modality': ",".join(selected_modalities),  # Verifique o nome da coluna!
                'wants_lunch': wants_lunch,
                'total': total,
                'paid': 0,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'version': 'alphaVersion'
            }

                    st.session_state['reg_data'] = reg_data

                    create_registration(name=name,modality=",".join(selected_modalities),wants_lunch=wants_lunch,total=total)

                    #------ DEBUG ----------
                    # st.write(st.session_state['reg_data'])
                    # st.write(reg_data['modality'])

                    st.session_state['currentPage'] = 'payment'
                    st.rerun()
                if config.Debug:
                    st.write('total:', total)
                    st.write(selected_modalities)

                    #st.session_state['currentPage'] = 'payment'
                else:
                    #st.session_state['currentPage'] = 'payment'
                    pass



        if config.Debug:
            if st.button("Voltar"):
                st.session_state['currentPage'] = 'home'
                st.rerun()


if __name__ == "__main__":
    main()