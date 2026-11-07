import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard Financeiro Familiar", layout="wide")

st.title("📊 Controle Financeiro Familiar")

# -----------------------------------------------------------------------------
# 1. Carregamento de Dados via Google Sheets (URL FIXA)
# -----------------------------------------------------------------------------
URL_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtiV86tR1oCqxRnZkyUTlM_tdo3hf6BSg0D1b2aK0b8RcBNCpiHQ-dRq_fYPO3kZRIg6xayfWzYecx/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def carregar_dados(url):
    try:
        df = pd.read_csv(url)
        df["Data"] = pd.to_datetime(df["Data"])
        return df
    except Exception as e:
        return None

df = carregar_dados(URL_SHEETS)

if df is None:
    st.error("Erro ao carregar os dados. Verifique se a planilha está publicada na web como CSV.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. Filtros Laterais
# -----------------------------------------------------------------------------
st.sidebar.header("Filtros")
membros_disponiveis = df["Membro"].unique() if "Membro" in df.columns else []
membros_selecionados = st.sidebar.multiselect(
    "Filtrar por Membro:",
    options=membros_disponiveis,
    default=membros_disponiveis
)

if membros_selecionados:
    df_filtrado = df[df["Membro"].isin(membros_selecionados)]
else:
    df_filtrado = df.copy()

# -----------------------------------------------------------------------------
# 3. Métricas Principais (KPIs)
# -----------------------------------------------------------------------------
total_receitas = df_filtrado[df_filtrado["Tipo"] == "Receita"]["Valor"].sum() if "Tipo" in df_filtrado.columns else 0.0
total_despesas = df_filtrado[df_filtrado["Tipo"] == "Despesa"]["Valor"].sum() if "Tipo" in df_filtrado.columns else 0.0
saldo = total_receitas - total_despesas

col1, col2, col3 = st.columns(3)
col1.metric("Total Entradas", f"R$ {total_receitas:,.2f}")
col2.metric("Total Saídas", f"R$ {total_despesas:,.2f}", delta_color="inverse")
col3.metric("Saldo do Período", f"R$ {saldo:,.2f}")

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. Gráficos Interativos
# -----------------------------------------------------------------------------
col_graf1, col_graf2 = st.columns(2)

df_despesas = df_filtrado[df_filtrado["Tipo"] == "Despesa"] if "Tipo" in df_filtrado.columns else pd.DataFrame()

with col_graf1:
    st.subheader("Gastos por Categoria")
    if not df_despesas.empty and "Categoria" in df_despesas.columns:
        fig_cat = px.pie(
            df_despesas, 
            values="Valor", 
            names="Categoria", 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.write("Nenhuma despesa encontrada.")

with col_graf2:
    st.subheader("Gastos por Integrante")
    if not df_despesas.empty and "Membro" in df_despesas.columns:
        fig_membro = px.bar(
            df_despesas, 
            x="Membro", 
            y="Valor", 
            color="Categoria" if "Categoria" in df_despesas.columns else None,
            barmode="group"
        )
        st.plotly_chart(fig_membro, use_container_width=True)
    else:
        st.write("Nenhuma despesa encontrada.")

# -----------------------------------------------------------------------------
# 5. Tabela Detalhada
# -----------------------------------------------------------------------------
st.subheader("Registro Detalhado de Transações")
st.dataframe(df_filtrado.sort_values(by="Data", ascending=False), use_container_width=True)
