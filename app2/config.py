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

currentVersion = 'alphaVersion1.2'

main_bg = NoBTImg
main_bg_ext = "png"

side_bg = NoBTImg
side_bg_ext = "png"

def custom_title_home():
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

def nobt_background_home():
    st.markdown("""
        <style>
        .stApp {
            background-image: url(https://raw.githubusercontent.com/bielbritob/DiaJogosForm/refs/heads/master/app2/assets/nobt2.png);;
            background-repeat: no-repeat;
            background-position: center;
            background-size: 700px;
            background-attachment: fixed;
            opacity: 1;
        }
    """, unsafe_allow_html=True)

def custom_title_register():
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

