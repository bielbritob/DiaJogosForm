import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1) Cria a conexão (lê .streamlit/secrets.toml automaticamente)
conn = st.connection("gsheets", type=GSheetsConnection)

spreadsheet = 'https://docs.google.com/spreadsheets/d/1aZQkfYMtZr0pAcSdL9l_-TFAdY5kcQzaM0XV8fmUoSs/edit?gid=0#gid=0'
# 2) Leitura (retorna pandas.DataFrame)
#df_regs = conn.read(worksheet="registrations", spreadsheet=spreadsheet)
#st.dataframe(df_regs)
#st.write(df_regs)

st.write(st.secrets)


