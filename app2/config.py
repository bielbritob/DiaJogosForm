import streamlit as st
import base64

PIX_KEY = "sua-chave-pix"
MERCHANT_NAME = "Terceirinhos"
MERCHANT_CITY = "Porto Velho"

modalidades = ["Vôlei", "Futsal", "Tênis de mesa", "Pebolim"]
price_modality = 5.0
price_marmita = 20.0

BANNER_HOME = 'app2/assets/banner_insta.jpg'

NoBTImg = 'app2/assets/nobtback.png'

Debug = False

main_bg = NoBTImg
main_bg_ext = "png"

side_bg = NoBTImg
side_bg_ext = "png"

def custom_title():
    st.markdown("""
                <h1 style="
                    font-family: 'Trebuchet MS', sans-serif;
                    text-align: center;
                    color: #ffffff;
                    font-size: 37px;
                    margin-top: -20px;
                    text-shadow: 0px 0px 20px blue;
                ">
                    Inscrição &mdash; Dia de Jogos Terceirão
                    <img src="https://cdn3.emoji.gg/emojis/9174-no-bitches-megamind.png" width="40" style="vertical-align: middle; margin-left: 10px;" />
                </h1>
            """, unsafe_allow_html=True)

def nobt_background():
    st.markdown("""
        <style>
        .stApp {
            background-image: url("app2\\assets\\banner_insta.jpg");;
            background-repeat: no-repeat;
            background-position: center;
            background-size: 700px;
            background-attachment: fixed;
            opacity: 1;
        }
    """, unsafe_allow_html=True)

def nobt2_background():
    main_bg = "sample.jpg"
    main_bg_ext = "jpg"

    side_bg = "sample.jpg"
    side_bg_ext = "jpg"

    st.markdown(
        f"""
        <style>
        .reportview-container {{
            background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()})
        }}
       .sidebar .sidebar-content {{
            background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()})
        }}
        </style>
        """,
        unsafe_allow_html=True
    )