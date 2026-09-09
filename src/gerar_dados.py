"""
gerar_dados.py

Gera um dataset ficticio de clientes Pessoa Juridica (PJ) de uma carteira
de gerencia bancaria, para uso no projeto de priorizacao de carteira.

Todos os dados sao sinteticos - nenhuma informacao real de cliente e usada.
"""

import numpy as np
import pandas as pd
from faker import Faker

# Reprodutibilidade: mesma "semente" sempre gera o mesmo dataset
SEED = 42
np.random.seed(SEED)
fake = Faker("pt_BR")
Faker.seed(SEED)

N_CLIENTES = 400

SETORES = ["Comércio", "Indústria", "Serviços", "Agronegócio", "Construção Civil"]
PESOS_SETORES = [0.35, 0.20, 0.30, 0.10, 0.05]  # distribuição realista de carteira PJ


def gerar_faturamento(n):
    """
    Simula faturamento anual concentrado entre 700k-800k,
    com cauda até 3M (distribuição lognormal).
    """
    valores = np.random.lognormal(mean=13.5, sigma=0.4, size=n)
    return np.clip(valores, 200_000, 3_000_000).round(2)


def gerar_dataset(n=N_CLIENTES):
    setores = np.random.choice(SETORES, size=n, p=PESOS_SETORES)
    faturamento = gerar_faturamento(n)

    dias_desde_contato = np.random.exponential(scale=25, size=n).astype(int)
    dias_desde_contato = np.clip(dias_desde_contato, 0, 180)

    tempo_relacionamento = np.random.randint(1, 180, size=n)  # meses

    # Produtos: quanto mais tempo de relacionamento, maior chance de ja ter produtos
    prob_produto_base = np.clip(tempo_relacionamento / 180, 0.1, 0.9)
    possui_conta_pj = np.ones(n, dtype=bool)  # todo cliente PJ tem conta
    possui_maquininha = np.random.random(n) < (prob_produto_base * 0.7)
    possui_credito_ativo = np.random.random(n) < (prob_produto_base * 0.5)
    possui_cartao_empresarial = np.random.random(n) < (prob_produto_base * 0.6)

    limite_credito_disponivel = (faturamento * np.random.uniform(0.02, 0.15, size=n)).round(2)

    # Atraso: a maioria em dia (0), poucos com atraso
    atraso_pagamento_dias = np.where(
        np.random.random(n) < 0.12,
        np.random.randint(1, 90, size=n),
        0
    )

    # Variacao de faturamento: maioria estavel/leve alta, poucos em queda forte
    variacao_faturamento_6m = np.round(np.random.normal(loc=2, scale=15, size=n), 1)

    nps_ultima_interacao = np.random.randint(0, 11, size=n)

    df = pd.DataFrame({
        "cliente_id": [f"PJ{str(i).zfill(4)}" for i in range(1, n + 1)],
        "razao_social": [fake.company() for _ in range(n)],
        "setor": setores,
        "faturamento_anual": faturamento,
        "dias_desde_ultimo_contato": dias_desde_contato,
        "possui_conta_pj": possui_conta_pj,
        "possui_maquininha": possui_maquininha,
        "possui_credito_ativo": possui_credito_ativo,
        "possui_cartao_empresarial": possui_cartao_empresarial,
        "limite_credito_disponivel": limite_credito_disponivel,
        "atraso_pagamento_dias": atraso_pagamento_dias,
        "variacao_faturamento_6m": variacao_faturamento_6m,
        "tempo_relacionamento_meses": tempo_relacionamento,
        "nps_ultima_interacao": nps_ultima_interacao,
    })

    return df


if __name__ == "__main__":
    df = gerar_dataset()
    output_path = "data/clientes_pj_simulado.csv"
    df.to_csv(output_path, index=False)
    print(f"Dataset gerado com {len(df)} clientes em '{output_path}'")
    print(df.head())
