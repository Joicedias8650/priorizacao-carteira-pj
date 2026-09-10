"""
scoring.py

Calcula o score de priorizacao de contato para cada cliente PJ da carteira,
combinando 3 dimensoes: urgencia de contato, oportunidade comercial e risco.

Score final: 0 (baixa prioridade) a 100 (alta prioridade).
"""

import pandas as pd
import numpy as np

# Pesos de cada dimensao (devem somar 1.0)
PESO_URGENCIA = 0.35
PESO_OPORTUNIDADE = 0.40
PESO_RISCO = 0.25


def _normalizar(serie: pd.Series) -> pd.Series:
    """Normaliza uma coluna para o intervalo 0-1 (min-max scaling)."""
    minimo, maximo = serie.min(), serie.max()
    if maximo == minimo:
        return pd.Series(0.5, index=serie.index)
    return (serie - minimo) / (maximo - minimo)


def calcular_score_urgencia(df: pd.DataFrame) -> pd.Series:
    """
    Quanto mais tempo sem contato, maior a urgencia.
    """
    return _normalizar(df["dias_desde_ultimo_contato"])


def calcular_score_oportunidade(df: pd.DataFrame) -> pd.Series:
    """
    Combina: produtos que o cliente NAO tem (potencial de cross-sell)
    e limite de credito disponivel nao utilizado.
    """
    produtos = ["possui_maquininha", "possui_credito_ativo", "possui_cartao_empresarial"]
    qtd_produtos_faltando = (~df[produtos]).sum(axis=1)  # 0 a 3
    score_produtos = qtd_produtos_faltando / 3

    score_limite = _normalizar(df["limite_credito_disponivel"])

    # Media simples entre as duas sub-dimensoes de oportunidade
    return (score_produtos + score_limite) / 2


def calcular_score_risco(df: pd.DataFrame) -> pd.Series:
    """
    Combina: atraso de pagamento e queda no faturamento recente.
    Quanto maior o risco, maior o score (cliente precisa de atencao).
    """
    score_atraso = _normalizar(df["atraso_pagamento_dias"])

    # Variacao negativa de faturamento = risco. Inverte o sinal e normaliza.
    queda_faturamento = (-df["variacao_faturamento_6m"]).clip(lower=0)
    score_queda = _normalizar(queda_faturamento)

    return (score_atraso + score_queda) / 2


def classificar_prioridade(df: pd.DataFrame) -> pd.Series:
    """
    Converte o score numerico em uma faixa categorica usando percentis,
    ja que os pesos combinados raramente produzem scores proximos de 100.
    Top 20% = Alta, proximos 30% = Media, restante = Baixa.
    """
    p80 = df["score_final"].quantile(0.80)
    p50 = df["score_final"].quantile(0.50)

    def _classificar(score):
        if score >= p80:
            return "Alta"
        elif score >= p50:
            return "Média"
        else:
            return "Baixa"

    return df["score_final"].apply(_classificar)


def calcular_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recebe o DataFrame de clientes e retorna uma copia com as colunas:
    score_urgencia, score_oportunidade, score_risco, score_final, prioridade.
    """
    df = df.copy()

    df["score_urgencia"] = calcular_score_urgencia(df)
    df["score_oportunidade"] = calcular_score_oportunidade(df)
    df["score_risco"] = calcular_score_risco(df)

    df["score_final"] = (
        PESO_URGENCIA * df["score_urgencia"]
        + PESO_OPORTUNIDADE * df["score_oportunidade"]
        + PESO_RISCO * df["score_risco"]
    ) * 100

    df["score_final"] = df["score_final"].round(1)
    df["prioridade"] = classificar_prioridade(df)

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/clientes_pj_simulado.csv")
    df_com_score = calcular_scores(df)

    colunas_exibicao = [
        "cliente_id", "razao_social", "setor", "faturamento_anual",
        "score_final", "prioridade"
    ]
    resultado = df_com_score[colunas_exibicao].sort_values("score_final", ascending=False)

    output_path = "data/clientes_pj_com_score.csv"
    df_com_score.to_csv(output_path, index=False)

    print(f"Scores calculados e salvos em '{output_path}'\n")
    print("Top 10 clientes prioritarios:")
    print(resultado.head(10).to_string(index=False))
