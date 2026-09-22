"""
test_scoring.py

Testes automatizados para a logica de calculo do score de priorizacao.
Rodar com: pytest tests/test_scoring.py
"""

import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from scoring import calcular_scores


@pytest.fixture
def df_exemplo():
    """
    Dataset pequeno e controlado, so para testar a logica -
    nao depende do CSV gerado pelo gerar_dados.py.
    """
    return pd.DataFrame({
        "cliente_id": ["PJ0001", "PJ0002", "PJ0003"],
        "razao_social": ["Empresa A", "Empresa B", "Empresa C"],
        "setor": ["Comércio", "Serviços", "Indústria"],
        "faturamento_anual": [800_000, 750_000, 1_200_000],
        "dias_desde_ultimo_contato": [5, 90, 30],
        "possui_conta_pj": [True, True, True],
        "possui_maquininha": [True, False, False],
        "possui_credito_ativo": [True, False, False],
        "possui_cartao_empresarial": [True, False, False],
        "limite_credito_disponivel": [10_000, 50_000, 30_000],
        "atraso_pagamento_dias": [0, 45, 0],
        "variacao_faturamento_6m": [5.0, -20.0, 2.0],
        "tempo_relacionamento_meses": [60, 12, 36],
        "nps_ultima_interacao": [9, 4, 7],
    })


def test_score_final_entre_0_e_100(df_exemplo):
    resultado = calcular_scores(df_exemplo)
    assert resultado["score_final"].between(0, 100).all()


def test_mais_dias_sem_contato_gera_maior_urgencia(df_exemplo):
    resultado = calcular_scores(df_exemplo)
    # PJ0002 tem 90 dias sem contato (o maior); PJ0001 tem 5 dias (o menor)
    score_urgencia_pj0002 = resultado.loc[resultado["cliente_id"] == "PJ0002", "score_urgencia"].iloc[0]
    score_urgencia_pj0001 = resultado.loc[resultado["cliente_id"] == "PJ0001", "score_urgencia"].iloc[0]
    assert score_urgencia_pj0002 > score_urgencia_pj0001


def test_atraso_de_pagamento_aumenta_score_de_risco(df_exemplo):
    resultado = calcular_scores(df_exemplo)
    # PJ0002 tem atraso de 45 dias e queda de faturamento; PJ0001 nao tem nenhum dos dois
    score_risco_pj0002 = resultado.loc[resultado["cliente_id"] == "PJ0002", "score_risco"].iloc[0]
    score_risco_pj0001 = resultado.loc[resultado["cliente_id"] == "PJ0001", "score_risco"].iloc[0]
    assert score_risco_pj0002 > score_risco_pj0001


def test_cliente_sem_produtos_tem_mais_oportunidade(df_exemplo):
    resultado = calcular_scores(df_exemplo)
    # PJ0002 e PJ0003 nao tem maquininha/credito/cartao; PJ0001 tem todos
    score_oportunidade_pj0002 = resultado.loc[resultado["cliente_id"] == "PJ0002", "score_oportunidade"].iloc[0]
    score_oportunidade_pj0001 = resultado.loc[resultado["cliente_id"] == "PJ0001", "score_oportunidade"].iloc[0]
    assert score_oportunidade_pj0002 > score_oportunidade_pj0001


def test_nao_ha_valores_nulos(df_exemplo):
    resultado = calcular_scores(df_exemplo)
    colunas_score = ["score_urgencia", "score_oportunidade", "score_risco", "score_final"]
    assert resultado[colunas_score].isna().sum().sum() == 0


def test_prioridade_so_tem_valores_validos(df_exemplo):
    resultado = calcular_scores(df_exemplo)
    valores_validos = {"Alta", "Média", "Baixa"}
    assert set(resultado["prioridade"].unique()).issubset(valores_validos)
