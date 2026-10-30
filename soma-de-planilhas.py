import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Sistema de Cálculo Automatizado", page_icon="📊", layout="wide")

st.title("📊 Sistema de Cálculo Automatizado")
st.markdown("Envie sua base de dados e clique em **Rodar Sistema** para processar o cálculo automático na coluna **E** (`(A * B + C) / D`).")

if "processado" not in st.session_state:
    st.session_state.processado = False

uploaded_file = st.file_uploader("Envie seu arquivo CSV", type=["csv"])

if uploaded_file is not None:
    st.success("📁 Arquivo enviado com sucesso! Pronto para processar.")

    if st.button("🚀 Rodar Sistema", type="primary"):
        try:
            df = pd.read_csv(uploaded_file)
        
            if df.shape[1] < 4:
                st.error("⚠️ O arquivo precisa ter pelo menos 4 colunas para representar A, B, C e D.")
            else:
                colA = df.columns[0]
                colB = df.columns[1]
                colC = df.columns[2]
                colD = df.columns[3]
                df['E'] = (df[colA] * df[colB] + df[colC]) / df[colD]

                st.session_state.df_resultado = df
                st.session_state.processado = True
                
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
if st.session_state.get("processado", False):
    st.markdown("---")
    st.success("✅ Cálculos realizados com sucesso para todas as linhas!")
    
    st.subheader("🎯 Resultado Processado:")
    st.dataframe(st.session_state.df_resultado, use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.df_resultado.to_excel(writer, index=False, sheet_name='Resultados')
    excel_data = output.getvalue()
    
    
    st.download_button(
        label="📥 Baixar Planilha Pronta (.xlsx)",
        data=excel_data,
        file_name="resultado_calculado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )