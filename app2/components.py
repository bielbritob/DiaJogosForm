import streamlit as st
import pandas as pd
import sqlite3

def registration_summary(reg):
    st.subheader("📋 Resumo da Inscrição")
    cols = st.columns([1, 2])
    with cols[0]:
        st.metric("Total a Pagar", f"R$ {reg['total']}")
        if str(reg['paid']) >= str(reg['total']):
            st.metric("Status", "✅ Pago")
        else:
            st.metric("Status",  "❌ Pendente")

    with cols[1]:
        st.write("**Modalidades:**")
        for mod in reg['modality'].split(','):
            st.write(f"- {mod} (R$ 5.00)")
        if reg['wants_lunch']:
            st.write("- 🍱 Marmita (R$ 20.00)")

    st.caption(f"Última atualização: {reg['updated_at']}")

def payment_history(reg_id):
    conn = sqlite3.connect("data.db")
    df = pd.read_sql("""
        SELECT created_at, amount, payload_hash 
        FROM payment_logs
        WHERE registration_id = ?
        ORDER BY created_at DESC
    """, conn, params=(reg_id,))
    conn.close()

    if not df.empty:
        st.subheader("📜 Histórico de Pagamentos")
        st.dataframe(df.style.format({'amount': 'R$ {:.2f}'}), use_container_width=True)