import streamlit as st
from db import init_db
from ui import show_form, show_payment_page
from config import DEBUG

st.set_page_config(page_title="Inscrição Dia de Jogos ADV", layout="centered", page_icon="🏐")
init_db()

if "step" not in st.session_state:
    st.session_state.step = "form"

st.checkbox("DEBUG?", value=DEBUG)

if st.session_state.step == "form":
    show_form()
elif st.session_state.step == "payment":
    show_payment_page(st.session_state.name, st.session_state.amount)
