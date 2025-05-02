import uuid
import streamlit as st
from components import registration_summary
from qrcode_utils import show_qr_code
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import config
from datetime import datetime
from time import sleep
from random import randint
from PIL import Image
import pytesseract
import re
from pypixmod import Pix
from zoneinfo import ZoneInfo
import random

def awesome_footer():
    # Estilos CSS customizados
    st.markdown("""
    <style>
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        color: white;
        text-align: center;
        padding: 15px;
        font-family: 'Courier New', monospace;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.2);
        z-index: 9999;
    }

    .footer span {
        animation: float 3s ease-in-out infinite;
        display: inline-block;
    }

    .footer a {
        color: #fff !important;
        text-decoration: none;
        margin: 0 5px;
        transition: all 0.3s ease;
    }

    .footer a:hover {
        text-shadow: 0 0 15px #ffffff;
        transform: scale(1.2);
    }

    #matrix-code {
        position: absolute;
        top: 0;
        left: 0;
        opacity: 0.1;
        pointer-events: none;
        font-size: 8px;
        color: #0f0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Efeito Matrix (opcional)
    matrix_code = "".join([str(randint(0, 1)) for _ in range(150)])

    # Conteúdo do footer
    st.markdown(f"""
    <div class="footer">
        <div id="matrix-code">{matrix_code}</div>
        <span>🚀</span> Developed with 
        <span style="animation-delay: 0.2s">❤️</span> by BIEL 
        <span style="animation-delay: 0.5s">✨</span> | 
        <a href="https://github.com/bielbritob" target="_blank">🔗 GitHub</a> | 
        <a href="instagram.com/bielbritober.w2">📧 Contact</a> | 
        {datetime.now().year} © Powered by Python Magic
    </div>
    """, unsafe_allow_html=True)


def matrix_footer():
    st.markdown("""
    <style>
    /* Efeito Matrix Azul */
    @keyframes matrix-rain {
        0% { transform: translateY(-100%); opacity: 1; }
        100% { transform: translateY(100vh); opacity: 0; }
    }

    .matrix-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 25px;
        overflow: hidden;
        z-index: 999;
        pointer-events: none;
    }

    .binary-code {
        position: absolute;
        color: #00f7ff;
        font-family: 'Courier New', monospace;
        font-size: 16px;
        text-shadow: 0 0 12px #0066ff;
        animation: matrix-rain 5s linear infinite;
        opacity: 1;
    }

    .cyber-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(0, 0, 0, 0.5);
        padding: 0px 0;
        text-align: center;
        border-top: 1px solid #0a00b3;
        z-index: 1000;
    }

    .dev-text {
        color: #00e6e6;
        font-family: 'Arial Black', sans-serif;
        letter-spacing: 1px;
        font-size: 6px;
    }

    .dev-text a {
        color: #14f0ff !important;
        text-decoration: none;
        transition: all 0.3s;
    }

    .dev-text a:hover {
        text-shadow: 0 0 12px #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

    # Generate animated binary streams
    binary_stream = []
    for i in range(25):  # number of streams
        left = random.randint(0, 95)
        delay = random.uniform(0, 5)
        length = random.randint(0, 5)
        code = "".join(str(random.randint(0, 1)) for _ in range(length))
        binary_stream.append(
            f"<div class='binary-code' style='left:{left}%; animation-delay:{delay}s; "  \
            f"animation-duration:{random.uniform(4,8)}s;'>" + code + "</div>"
        )

    # Render footer and matrix
    st.markdown(f"""
    <div class='matrix-container'>
        {''.join(binary_stream)}
    </div>
    <div class='cyber-footer'>
        <span class='dev-text'>
            DEVELOPED BY <a href='https://www.instagram.com/bielbritober.w2/' target='_blank'>BIEL</a>
        </span>
    </div>
    """, unsafe_allow_html=True)


def animated_toast(message, delay=0.05):
    toast_container = st.empty()
    full_message = ""
    for char in message:
        full_message += char
        toast_container.toast(full_message + " ▌", icon="⌨️")
        sleep(delay)
    return full_message


def _get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

tz = ZoneInfo("America/Manaus")
def create_registration(name: str, modality: str, wants_lunch: bool, total: float):
    conn = st.connection("gsheets", type=GSheetsConnection)

    try:
        # Ler dados existentes
        df_existing = conn.read(worksheet="registrations", ttl=0) # ttl = 0 para ele nao salvar dados antigos
        #st.dataframe(df_existing)
        # Criar novo registro
        new_id = str(uuid.uuid4())
        new_version = 'alphaVersion1.0'

        new_row = pd.DataFrame([{
            "name": name,
            "modality": modality,
            "wants_lunch": int(wants_lunch),
            "total": total,
            "paid": 0,
            "paid_value": 0,
            "is_active": 1,
            "created_at": datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),
            "version": new_version
        }])

        # Juntar com dados existentes e salvar
        df_updated = pd.concat([df_existing, new_row], ignore_index=True)
        conn.update(worksheet="registrations", data=df_updated)

    except Exception as e:
        st.error(f"Erro ao criar registro: {str(e)}")
        raise


def edit_registration(name: str, modality: str, wants_lunch: bool, total: float, paid: float, paid_value: float):
    conn = st.connection("gsheets", type=GSheetsConnection)

    try:
        # Ler dados existentes
        df_existing = conn.read(worksheet="registrations", ttl=0)
        new_version = config.currentVersion

        # Criar nova linha com dados atualizados
        new_data = {
            "name": name,
            "modality": modality,
            "wants_lunch": int(wants_lunch),
            "total": total,
            "paid": paid,
            "paid_value": paid_value,
            "is_active": 1,
            "updated_at": datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),
            "version": new_version
        }

        # Verificar se o nome já existe na planilha
        if not df_existing.empty and name in df_existing['name'].values:
            # Atualizar linha existente
            idx = df_existing.index[df_existing['name'] == name].tolist()[0]
            # Manter created_at original
            new_data["created_at"] = df_existing.loc[idx, "created_at"]
            # Atualizar dados
            df_existing.loc[idx] = {**df_existing.loc[idx].to_dict(), **new_data}
        else:
            # Adicionar nova linha (caso seja um novo registro)
            new_data["created_at"] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            df_existing = pd.concat([df_existing, pd.DataFrame([new_data])], ignore_index=True)

        # Salvar dados atualizados na planilha
        conn.update(worksheet="registrations", data=df_existing)

    except Exception as e:
        st.error(f"Erro ao editar registro: {str(e)}")
        raise


def create_registration_old(name: str, modality: str, wants_lunch: bool, total: float):
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
    new_id = str(datetime.now(tz).timestamp())
    new_version = 1 if reg_df.empty else reg_df[reg_df["name"] == name]["version"].max() + 1

    new_reg = pd.DataFrame([{
        "name": name,
        "modality": modality,
        "wants_lunch": int(wants_lunch),
        "total": total,
        "paid": 0,
        "created_at": datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),
        "version": config.currentVersion,
        "is_active": 1,
    }])

    conn.update(worksheet="registrations", data=new_reg)

    # Log de alteração
    changes_df = pd.DataFrame([{
        "registration_name": name,
        "old_value": f"{total}",
        "new_value": f"Created v{new_version}", #por logica pagou x falta y
        "changed_by": "system",
        "created_at": datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    }])

    conn.update(worksheet="registrationsChanges", data=changes_df)
    conn.create()
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

        df = conn.query(sql=sql, ttl=0)


        if not df.empty:
            # Mapeamento das colunas para o formato esperado
            row = df.iloc[0]

            raw = get_nounce(row['name'])
            nounce_value = raw["nounce"] if raw is not None else None

            return {
                'name': row['name'],
                'modality': row['modality'],  # Verifique o nome da coluna!
                'wants_lunch': bool(row['wants_lunch']),
                'total': row['total'],
                'paid': row['paid'],
                'paid_value': row['paid_value'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'version': row['version'],
                'nounce': nounce_value
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


def get_nounce(name: str):
    conn = _get_conn()
    sql = f"""
         SELECT *
         FROM paymentLogs
         WHERE name = '{name}'
         ORDER BY created_at ASC
         LIMIT 1
       """
    df = conn.query(sql=sql, ttl=0)
    if not df.empty:
        row = df.iloc[0]
        return {
            "name": row["name"],
            "nounce": int(row["nounce"]),
            "created_at": row["created_at"]
        }
    return None



def log_payment_attempt(name: str, nounce: int, created_at: str, updated_at: str):
    conn = _get_conn()
    df_existing_log = conn.read(worksheet="paymentLogs", ttl=0)

    # prepare new row
    new_row = pd.DataFrame([{
        "name": name,
        "nounce": nounce,
        "created_at": created_at,
        "updated_at": updated_at,
    }])

    if not df_existing_log.empty and name in df_existing_log['name'].values:
        # update existing
        idx = df_existing_log.index[df_existing_log['name'] == name][0]
        # preserve original created_at
        original = df_existing_log.at[idx, 'created_at']
        row = new_row.iloc[0].to_dict()
        row['created_at'] = original
        df_existing_log.loc[idx] = row
    else:
        # append
        df_existing_log = pd.concat([df_existing_log, new_row], ignore_index=True)

    conn.update(worksheet="paymentLogs", data=df_existing_log)


def generate_pix_payload(chave_pix: str, amount: float, nounce: int):
    # Testado e funcionando para Nubank, Inter, Caixa, Mercadopago
    pix.set_name_receiver('Financeiro Terceirinhos')
    pix.set_city_receiver('Porto Velho')
    pix.set_key(chave_pix)
    pix.set_identification(f'{nounce}')
    # pix.set_zipcode_receiver('78906520')
    pix.set_description(f'Pagamento Inscrição DiaDJogos Terceirinhos {nounce} ')
    pix.set_amount(amount)

    print(pix.identification)
    print('\nDonation with defined amount - PYPIX >>>>\n', pix.get_br_code())
    return pix.get_br_code()


def generate_and_store_nounce():
    nounce = random.randint(100000, 999999)
    #conn = _get_conn()
    # Atualiza a planilha na linha de reg['id']:
    #df_existing = conn.read(worksheet="paymentLogs", ttl=0)

    # conn.update(
    #    worksheet="paymentLogs",
    #    data=[{"name": reg["name"], "nounce": nounce, "created": reg['created_at']}]
    # )
    #st.session_state['reg_data']["nounce"] = str(nounce)
    return nounce

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

        #awesome_footer()
        matrix_footer()

        config.nobt_background_home()

        with st.form("main_form"):
            name = str(st.text_input("Nome Completo").strip())

            if st.form_submit_button("Avançar"):
                if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', name):  # Validação com regex
                    st.error("O nome deve conter apenas letras e espaços!")

                elif name != "":
                    #reg = get_active_registration(name)

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
        matrix_footer()
        reg = st.session_state['reg_data']
        tab_pay, tab_edit = st.tabs(["Pagamento", "Editar Inscrição"])

        with tab_pay:
            registration_summary(reg)
            if st.session_state['reg_data']['paid'] != 1:

                #if 'nounce' not in st.session_state['reg_data']:
                #    st.session_state['reg_data']['nounce'] = generate_and_store_nounce(reg)

                nounce = st.session_state['reg_data']['nounce']

                total = float(reg['total'])
                paid_value = float(reg.get('paid_value'))

                pendent = total - paid_value
                payload = generate_pix_payload(chave_pix=config.PIX_KEY, amount=pendent, nounce=nounce)
                log_payment_attempt(name=reg['name'],
                                    nounce=nounce,
                                    created_at=st.session_state['reg_data']['created_at'],
                                    updated_at=datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"))

                img_bytes = show_qr_code(payload)
                st.image(img_bytes, caption="QR Code PIX", output_format='PNG')

                #st.badge("chave pix alternativa:", color='gray')
                #st.code("lcamille603@gmail.com")



                #--------- Validacao Pagamento -----------
                st.markdown("---")
                st.subheader("Envie um comprovante (imagem/pdf) para validação OCR")
                st.markdown("""
                <div style="
                    background-color: #5c5000;
                    border-left: 5px solid #ffa500;
                    padding: 12px 16px;
                    border-radius: 4px;
                    color: #bec24a;
                    font-family: Arial, sans-serif;
                    margin-bottom: 1rem;
                ">
                  <strong style="font-size:1.1em;">⚠️ Para validar seu comprovante, ele deve conter:</strong>
                  <ul style="margin:8px 0 0 1.2em; padding: 0; list-style-type: disc;">
                    <li><span style="font-weight:600;">Valor</span> (R$ XX,XX)</li>
                    <li><span style="font-weight:600;">Recebedor</span> (nome da chave PIX)</li>
                    <li><span style="font-weight:600;">Tipo de Transferência</span> (deve aparecer “Pix”)</li>
                    <li><span style="font-weight:600;">Identificador / Detalhes</span> (código de 6 dígitos)</li>
                  </ul>
                </div>
                """, unsafe_allow_html=True)
                uploaded = st.file_uploader("Comprovante", type=["png", "jpg", "jpeg"])


                #================ DEBUG LOCAL ONLY ===================
                #pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
                pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
                # --- funcoes de parsing ---
                # padrões da sua descrição de payload
                KEYWORDS_DESC = ["DiaDJogos", "Terceirinhos", "PYPIX", "Pix"]

                def parse_receipt_value(text):
                    # Força o texto para minúsculas para padronizar buscas
                    text = text.lower()

                    # Tenta encontrar padrão "valor" seguido de um número (pode estar na linha seguinte)
                    valor_match = re.search(r"valor[\s:\n\r]*([\d]{1,3}(?:[.,]\d{2}))", text)
                    if valor_match:
                        valor_str = valor_match.group(1).replace(',', '.')
                        return float(valor_str)

                    # Se não encontrou via "valor", procura por "R$ XX,XX"
                    r_match = re.search(r"r\$[\s]*([\d]{1,3}(?:[.,]\d{2}))", text)
                    if r_match:
                        valor_str = r_match.group(1).replace(',', '.')
                        return float(valor_str)

                    return None

                def parse_receipt_receiver(text):
                    patterns = [
                        r"Para\s+([A-ZÀ-Ÿ0-9 ].{3,})",
                        r"Destino\s+Nome\s+([A-ZÀ-Ÿ ].+)",
                        r"Quem recebeu\s+Nome\s+([A-ZÀ-Ÿ ].+)"
                    ]
                    for p in patterns:
                        m = re.search(p, text, flags=re.IGNORECASE)
                        if m:
                            return m.group(1).strip()
                    return None

                def parse_receipt_type(text):
                    # 1) tenta rótulo “Pix”
                    m = re.search(r"Tipo de transferência\s*[:\-]?\s*(Pix|PIX)", text, flags=re.IGNORECASE)
                    if m:
                        return "PIX"
                    # 2) tenta título “Pix enviado”
                    if re.search(r"Pix enviado", text, flags=re.IGNORECASE):
                        return "PIX"
                    # 3) tenta encontrar alguma das keywords da sua descrição
                    for kw in KEYWORDS_DESC:
                        if re.search(re.escape(kw), text, flags=re.IGNORECASE):
                            return kw
                    return None

                def parse_nounce(text):
                    # Tenta pegar diretamente após a palavra 'Identificador'
                    m = re.search(r"Identificador\s*[:\-]?\s*(\d{6})", text, flags=re.IGNORECASE)
                    if m:
                        return m.group(1)
                    # fallback: qualquer número de 6 dígitos isolado
                    m = re.search(r"\b(\d{6})\b", text)
                    return m.group(1) if m else None


                if uploaded:
                    # Carrega imagem
                    if uploaded.type.startswith("image"):
                        img = Image.open(uploaded)
                    else:
                        from pdf2image import convert_from_bytes
                        pages = convert_from_bytes(uploaded.read())
                        img = pages[0]
                    if config.Debug:
                        st.image(img, caption="Comprovante recebido", width=300)

                    # OCR
                    text = pytesseract.image_to_string(img, lang="por")
                    if config.Debug:
                        st.text_area("Texto extraído (OCR)", text, height=200)

                    total = reg["total"]

                    val = parse_receipt_value(text)
                    receiver = parse_receipt_receiver(text)
                    ttype = parse_receipt_type(text)

                    # condiçõe


                    # …e na hora de validar:
                    ok_valor = (val is not None and val == pendent)
                    # ajuste aqui os nomes reais que você espera no recebedor
                    ok_receiver = receiver and ("FINANCEIRO" in receiver.upper() or "FRANCISCA" in receiver.upper())
                    # considera válido se tiver PIX ou qualquer keyword da descrição
                    ok_type = (ttype == "PIX") or (ttype in KEYWORDS_DESC)

                    # obtém o nounce armazenado (int)
                    stored = get_nounce(reg['name'])
                    stored_nounce = stored["nounce"] if stored else None

                    # extrai do OCR (string) e tenta converter para int
                    extracted = parse_nounce(text)
                    try:
                        extracted_nounce = int(extracted) if extracted is not None else None
                    except ValueError:
                        extracted_nounce = None

                    ok_nounce = (extracted_nounce is not None
                                 and stored_nounce is not None
                                 and extracted_nounce == stored_nounce)
                    # mensagens ao usuário
                    if val is None:
                        st.error("❌ Não achei valor R$ XX,XX no comprovante.")
                    else:
                        st.write(f"🔍 Valor detectado: R$ {val:.2f}")
                        if not receiver:
                            st.warning("⚠️ Não consegui identificar o nome do recebedor.")
                        else:
                            st.write(f"🔍 Recebedor detectado: **{receiver}**")
                        if not ok_type:
                            st.warning(f"⚠️ Não detectei PIX nem descrição esperada.")
                        if not ok_nounce:
                            st.warning(f"⚠️ Não detectei NOUNCE!")
                            st.write(ok_nounce)
                        if ok_valor and ok_receiver and ok_type and ok_nounce:
                            st.success("✅ Comprovante validado com sucesso! Atualizando status…")
                            st.info("Relogue para atualizar Status!")
                            edit_registration(
                                name=st.session_state['reg_data']['name'],
                                modality=st.session_state['reg_data']['modality'],
                                wants_lunch=st.session_state['reg_data']['wants_lunch'],
                                total=st.session_state['reg_data']['total'],
                                paid=1,
                                paid_value=st.session_state['reg_data']['total'] ++ st.session_state['reg_data']['paid_value']
                            )

                        else:
                            msgs = []
                            if not ok_valor:    msgs.append(f"Valor ({val:.2f}) não confere com {pendent:.2f}")
                            if not ok_receiver: msgs.append(f"Recebedor ({receiver}) não confere")
                            if not ok_type:     msgs.append("Não detectei PIX ou descrição válida")
                            st.error("❌ Validação falhou:\n"  + ";""\n".join(msgs))

                else:
                    st.info("Faça upload de um comprovante para iniciar o teste.")
            else:
                pass


        with tab_edit:
            with st.form("edit_form"):
                col1 , col2 = st.columns([5,1],vertical_alignment='top')
                with col1:
                    st.title("📋 Editar Inscrição")

                name = st.text_input("Nome Completo", value=st.session_state['reg_data']['name'],disabled=True).strip()

                selected_modalities = st.pills(f"Modalidades já escolhida (R$ {int(config.price_modality)},00 cada)", st.session_state['reg_data']['modality'].split(","), selection_mode='multi', default=st.session_state['reg_data']['modality'].split(","), disabled=True)

                available_modalities = [m for m in config.modalidades if m not in selected_modalities]

                if available_modalities:  # Só mostra se houver opções disponíveis
                    new_modalities = st.pills(
                        f"Modalidades ainda disponíveis (R$ {int(config.price_modality)},00 cada)", options=available_modalities, selection_mode='multi'
                    )

                    # Atualiza a lista combinando antigas + novas (sem duplicatas)
                    updated_modalities = list(set(selected_modalities + new_modalities))

                    st.session_state['reg_data']['modality'] = ",".join(updated_modalities)

                else:
                    pass

                if st.session_state['reg_data']['wants_lunch'] == 0:
                    wants_lunch = st.checkbox(
                        f"Adicionar marmita (R$ {int(config.price_marmita)},00)", value=st.session_state['reg_data']['wants_lunch'])
                else:
                    wants_lunch = st.checkbox(
                        f"Adicionar marmita (R$ {int(config.price_marmita)},00)",
                        value=st.session_state['reg_data']['wants_lunch'], disabled=True)

                total = st.session_state['reg_data']['total']
                if config.Debug:
                    st.write(len(st.session_state['reg_data']['modality'].split(",")))
                    st.write(st.session_state['reg_data']['wants_lunch'])
                if len(st.session_state['reg_data']['modality'].split(",")) == 4 and st.session_state['reg_data']['wants_lunch'] == True:
                    if st.form_submit_button("Confirmar Edição", disabled=True):
                        pass
                    # Efeito visual especial
                    with st.container():
                        st.empty()  # Espaço em branco para melhor layout

                        # Fogos de artifício ASCII animados
                        st.markdown("""
                                                <style>
                                                @keyframes explode {
                                                    0% { opacity: 0; transform: translateY(0); }
                                                    50% { opacity: 1; transform: translateY(-20px); }
                                                    100% { opacity: 0; transform: translateY(-40px); }
                                                }
                                                .firework {
                                                    animation: explode 1.5s infinite;
                                                    display: inline-block;
                                                    margin: 0 5px;
                                                }
                                                </style>
                                                """, unsafe_allow_html=True)

                        fireworks = ["✨", "🎇", "🎆", "💥", "🔥", "🌟"]
                        cols = st.columns(10)
                        for col in cols:
                            with col:
                                for _ in range(3):
                                    st.markdown(
                                        f'<div class="firework" style="animation-delay:{randint(0, 1000)}ms">{fireworks[randint(0, 5)]}</div>',
                                        unsafe_allow_html=True)

                        # Mensagem principal com efeito de digitação
                        message = animated_toast("🐉 A LENDA DO JOGO! Você é o(a) MVP completo(a) 🏆", 0.05)
                        sleep(0.5)

                        # Card especial
                        st.markdown(f"""
                                                <div style='
                                                    padding: 2rem;
                                                    background: linear-gradient(45deg, #00f7ff, #4059ff);
                                                    border-radius: 15px;
                                                    color: white;
                                                    text-align: center;
                                                    box-shadow: 0 10px 20px rgba(0,0,0,0.5);
                                                    margin: 2rem 0;
                                                    animation: fadeIn 1s ease-in;
                                                '>
                                                    <h1 style='font-size: 2.5rem; margin: 0;'>🏅 OBRIGADO POR SER 100%! 🏅</h1>
                                                    <p style='font-size: 1.2rem;'>Sua energia transforma o evento! Prepare-se para:</p>
                                                    <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 2rem 0;'>
                                                        <div style='padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px;'>
                                                            🥇 Melhores Partidas
                                                        </div>
                                                        <div style='padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px;'>
                                                            🍔 Almoço Épico
                                                        </div>
                                                        <div style='padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px;'>
                                                            🎉 Muita Diversão
                                                        </div>
                                                    </div>
                                                    <p style='font-size: 1.5rem; margin: 0;'>Nos vemos no evento, Campeão(a)! 💪</p>
                                                </div>
                                                """, unsafe_allow_html=True)

                        # Efeitos adicionais
                        st.balloons()
                        sleep(1)
                        st.balloons()
                        sleep(1)
                        st.balloons()
                        sleep(1)
                        st.balloons()

                        # Toque final com emojis animados
                        st.toast("🚀 Você acaba de desbloquear o modo FULL POWER!", icon="🎮")
                        sleep(1)
                        st.toast("🌟 Dica: Traga sua energia e prepare-se para brilhar!", icon="💡")
                else:
                    if st.form_submit_button("Confirmar Edição"):
                        if not selected_modalities:
                            st.error("Selecione ao menos uma modalidade")
                        else:
                            total = len(updated_modalities) * config.price_modality
                            if wants_lunch:
                                total += config.price_marmita

                        reg_data = {
                    'name': name,
                    'modality': st.session_state['reg_data']['modality'],  # Verifique o nome da coluna!
                    'wants_lunch': wants_lunch,
                    'total': total,
                    'paid': 0,
                    "paid_value": st.session_state['reg_data']['paid_value'],
                    'created_at': st.session_state['reg_data']['created_at'],
                    'updated_at': datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),
                    'version': config.currentVersion,
                    'nounce': st.session_state['reg_data']['nounce']
                }

                        st.session_state['reg_data'] = reg_data

                        edit_registration(
                            name=st.session_state['reg_data']['name'],
                            modality=reg_data['modality'],
                            wants_lunch=st.session_state['reg_data']['wants_lunch'],
                            total=st.session_state['reg_data']['total'],
                            paid=st.session_state['reg_data']['paid'],
                            paid_value=st.session_state['reg_data']['paid_value']
                        )

                        st.info("Salvando...")
                        st.rerun()
        if st.button("Voltar Home"):
            st.session_state['currentPage'] = 'home'
            st.session_state['reg_data'] = None
            st.rerun()

    elif st.session_state['currentPage'] == 'register':
        config.custom_title_register()
        st.divider()
        #awesome_footer()
        matrix_footer()
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
                'paid_value': 0,
                'created_at': datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),
                'version': config.currentVersion,
                'nounce': generate_and_store_nounce()
            }

                    st.session_state['reg_data'] = reg_data

                    create_registration(name=name,modality=st.session_state['reg_data']['modality'],wants_lunch=wants_lunch,total=total)

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
    pix = Pix()
    main()