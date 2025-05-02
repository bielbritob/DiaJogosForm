import streamlit as st
import pandas as pd

def registration_summary(reg):
    # Garante conversão para float
    total = float(reg['total'])
    paid_value = float(reg.get('paid_value')) ###############

    st.subheader("📋 Resumo da Inscrição")
    cols = st.columns([1, 2])
    with cols[0]:
        # Mostra total vs pago
        st.metric("Total a Pagar", f"R$ {total:.2f}")
        # Exibe valor já pago
        if paid_value > 0:
            st.metric("Já Pago", f"R$ {paid_value:.2f}")
            st.write("---")
        # Status geral
        if paid_value >= total:
            status = "✅ Pago"
            st.success(f"🎉 Pagamento concluído! Recebemos R$ {paid_value:.2f}.")
        elif paid_value > 0:
            restante = total - paid_value
            status = "⚠️ Parcial"
            st.warning(f"Você já pagou R$ {paid_value:.2f}. \n \n Faltam R${restante:.2f} para completar.")

        else:
            status = "❌ Pendente"
            st.info(
                "Após efetuar o pagamento via PIX, valide seu comprovante.\n"
                "Seu status mudará para Pago assim que validarmos.")
        st.metric("Status", status)

    with cols[1]:
        st.write("**Modalidades:**")
        # Lista de modalidades
        for mod in reg['modality'].split(","):
            st.write(f"- {mod} (R$ 5.00)")
        if reg['wants_lunch']:
            st.write("- 🍱 Marmita (R$ 20.00)")

    st.caption(f"Última atualização: {reg['updated_at']}")

def payment_history(reg_id):
    # Obtém a conexão com o Google Sheets
    conn = st.connection("gsheets", type="gsheets")

    try:
        # Lê todos os registros da planilha de pagamentos
        df = conn.read(worksheet="payment_logs")

        # Filtra pelo ID de registro
        if not df.empty:
            # Converte para string para evitar problemas de tipo
            df = df[df['registration_id'].astype(str) == str(reg_id)]

            # Formata a exibição
            df = df.sort_values('created_at', ascending=False)
            df = df[['created_at', 'amount', 'payload_hash']]  # Seleciona colunas relevantes

        if not df.empty:
            st.subheader("📜 Histórico de Pagamentos")

            # Formatação monetária
            styled_df = df.style.format({
                'amount': 'R$ {:.2f}',
                'created_at': lambda x: x.strftime('%d/%m/%Y %H:%M') if not pd.isnull(x) else ''
            })

            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("Nenhum pagamento registrado ainda.")

    except Exception as e:
        st.error(f"Erro ao carregar histórico: {str(e)}")