# Painel de Priorização de Carteira PJ

Projeto de portfólio (Dados/Analytics/BI) que simula uma carteira de clientes Pessoa Jurídica de gerência bancária e gera um score de priorização de contato, resolvendo o problema real de decisão fragmentada entre múltiplos sistemas.

## 1. Objetivo do projeto

Construir um pipeline de dados completo — geração/tratamento de dados, cálculo de score, dashboard interativo — que responda à pergunta: **"de todos os meus clientes, com quem eu deveria falar hoje, e por quê?"**

Isso demonstra, num único projeto:
- Modelagem de dados (schema de negócio bancário PJ)
- ETL (Extract, Transform, Load) com Python/pandas
- Lógica de regras de negócio → score
- Visualização de dados (dashboard)
- Boas práticas de projeto (repo organizado, README, versionamento)

## 2. Dataset simulado

Como os dados são fictícios, gere com Python (`faker` + `numpy`/`pandas`) uma tabela `clientes_pj.csv` com ~300-500 linhas e as colunas abaixo.

| Coluna | Tipo | Descrição |
|---|---|---|
| `cliente_id` | string | Identificador único (fictício) |
| `razao_social` | string | Nome fictício da empresa (faker) |
| `setor` | categórico | Comércio, Indústria, Serviços, Agro, etc. |
| `faturamento_anual` | float | Simular concentração entre R$700k–R$3M (distribuição normal/lognormal) |
| `dias_desde_ultimo_contato` | int | Simula o "giro de carteira" |
| `possui_conta_pj` | bool | Produto ativo |
| `possui_maquininha` | bool | Produto ativo |
| `possui_credito_ativo` | bool | Produto ativo |
| `possui_cartao_empresarial` | bool | Produto ativo |
| `limite_credito_disponivel` | float | Simula oportunidade de oferta |
| `atraso_pagamento_dias` | int | 0 se em dia; >0 simula risco |
| `variacao_faturamento_6m` | float | % de queda/alta simulada (sinal de risco ou de crescimento) |
| `tempo_relacionamento_meses` | int | Tempo como cliente do banco |
| `nps_ultima_interacao` | int (opcional) | 0–10, simula satisfação |

**Dica de geração:** use `numpy.random` com distribuições que imitem a realidade que você descreveu (faturamento médio 700-800k com cauda até 3M), e injete correlações propositais (ex: setores de comércio com mais sazonalidade, clientes com mais tempo de relacionamento tendo mais produtos) para o dashboard contar uma história coerente.

## 3. Lógica do score de priorização

Um score de 0 a 100 combinando 3 dimensões, com pesos ajustáveis (isso também é um ótimo ponto pra explicar em entrevista — "eu desenhei os pesos assim, e poderiam ser calibrados com dados reais/regressão no futuro"):

**a) Urgência de contato (peso 35%)**
- Baseado em `dias_desde_ultimo_contato` normalizado (quanto mais tempo sem contato, maior a urgência)

**b) Oportunidade comercial (peso 40%)**
- Produtos que o cliente NÃO tem × faturamento (potencial de cross-sell)
- Limite de crédito disponível não utilizado

**c) Risco (peso 25%)**
- `atraso_pagamento_dias` > 0 → aumenta prioridade (mas como "risco", não "oportunidade")
- `variacao_faturamento_6m` negativa → sinal de alerta

```python
score = (0.35 * score_urgencia) + (0.40 * score_oportunidade) + (0.25 * score_risco)
```

Cada sub-score é normalizado (0-1) antes de compor a fórmula. Depois classifique em faixas: **Alta / Média / Baixa prioridade**.

## 4. Stack técnica sugerida

- **Python 3.11+**
- `pandas` — manipulação de dados
- `faker` — geração de dados fictícios realistas
- `numpy` — distribuições estatísticas
- `streamlit` — dashboard interativo (mais rápido de montar que Power BI/Dash pra portfólio solo)
- `plotly` ou `matplotlib` — gráficos dentro do Streamlit
- `pytest` (opcional, mas soma muito) — testes da função de score

## 5. Estrutura do repositório

```
priorizacao-carteira-pj/
├── README.md
├── requirements.txt
├── data/
│   └── clientes_pj_simulado.csv
├── src/
│   ├── gerar_dados.py       # script que cria o dataset fictício
│   ├── scoring.py            # lógica de cálculo do score
│   └── dashboard.py          # app Streamlit
├── notebooks/
│   └── exploracao.ipynb      # EDA (análise exploratória) — mostra raciocínio
└── tests/
    └── test_scoring.py
```

## 6. Roteiro de construção (passo a passo)

1. `gerar_dados.py` — gera e salva o CSV simulado
2. `notebooks/exploracao.ipynb` — EDA: distribuições, correlações, gráficos exploratórios (mostra pensamento analítico)
3. `scoring.py` — funções puras de cálculo de cada sub-score e do score final
4. `test_scoring.py` — testes simples (ex: cliente com maior atraso deve ter score de risco maior)
5. `dashboard.py` — Streamlit com:
   - Tabela ordenada por score (quem contatar primeiro)
   - Filtros por setor/faixa de faturamento
   - Gráfico de distribuição de prioridades
   - Ao clicar num cliente, ver o "porquê" do score (explicabilidade — isso impressiona muito em entrevista)
6. `README.md` — contextualize o problema de negócio (a fragmentação de sistemas que você vive), sem citar o Bradesco nominalmente nem nada sensível — fale em termos genéricos de "gestão de carteira PJ em banco de varejo"

## 7. Cuidados de compliance (importante)

- Nunca usar nomes reais de clientes, CNPJs reais, ou qualquer dado que possa ser rastreado à carteira real
- Não mencionar o nome do banco de forma que sugira uso de sistemas/dados internos
- Deixe claro no README que é um projeto conceitual com dados 100% sintéticos, inspirado em um problema real do setor bancário

## 8. Próximos passos possíveis (evolução do projeto)

- Trocar as regras de score por um modelo de machine learning simples (regressão logística) treinado num "histórico simulado de contatos e resultados"
- Adicionar um segundo módulo simulando alertas automáticos (ex: "cliente com 20% de queda de faturamento nos últimos 3 meses")
