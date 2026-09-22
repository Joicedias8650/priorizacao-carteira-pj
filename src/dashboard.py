"""
dashboard.py

Dashboard interativo (Streamlit) que exibe a carteira de clientes PJ
ordenada por score de priorizacao, com filtros basicos.

Para rodar:
    streamlit run src/dashboard.py
"""

import pandas as pd
import streamlit as st
from scoring import calcular_scores

st.set_page_config(page_title="Priorização de carteira PJ", layout="wide")

st.title("Painel de priorização de carteira PJ")
st.caption("Quem contatar hoje, e por quê — carteira simulada.")


@st.cache_data
def carregar_dados():
    df = pd.read_csv("data/clientes_pj_simulado.csv")
    return calcular_scores(df)


df = carregar_dados()

# --- Filtros na barra lateral ---
st.sidebar.header("Filtros")

setores = st.sidebar.multiselect(
    "Setor",
    options=sorted(df["setor"].unique()),
    default=sorted(df["setor"].unique()),
)

prioridades = st.sidebar.multiselect(
    "Prioridade",
    options=["Alta", "Média", "Baixa"],
    default=["Alta", "Média", "Baixa"],
)

df_filtrado = df[df["setor"].isin(setores) & df["prioridade"].isin(prioridades)]

# --- Métricas resumo ---
col1, col2, col3 = st.columns(3)
col1.metric("Clientes na visão", len(df_filtrado))
col2.metric("Alta prioridade", (df_filtrado["prioridade"] == "Alta").sum())
col3.metric("Score médio", round(df_filtrado["score_final"].mean(), 1))

# --- Gráfico: quantidade por faixa de prioridade ---
st.subheader("Distribuição por prioridade")
contagem = df_filtrado["prioridade"].value_counts().reindex(["Alta", "Média", "Baixa"])
st.bar_chart(contagem)

# --- Tabela principal ---
st.subheader("Clientes ordenados por prioridade")

colunas_exibicao = [
    "cliente_id", "razao_social", "setor", "faturamento_anual",
    "dias_desde_ultimo_contato", "score_final", "prioridade",
]

tabela = df_filtrado[colunas_exibicao].sort_values("score_final", ascending=False)
st.dataframe(tabela, use_container_width=True, hide_index=True)

# --- Detalhe de um cliente (o "porquê" do score) ---
st.subheader("Ver detalhe de um cliente")
cliente_escolhido = st.selectbox("Cliente", df_filtrado["cliente_id"])

if cliente_escolhido:
    linha = df_filtrado[df_filtrado["cliente_id"] == cliente_escolhido].iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Urgência", f'{linha["score_urgencia"]:.0%}')
    c2.metric("Oportunidade", f'{linha["score_oportunidade"]:.0%}')
    c3.metric("Risco", f'{linha["score_risco"]:.0%}')
    st.caption(
        f'Score final: {linha["score_final"]} → prioridade {linha["prioridade"]}'
    )
