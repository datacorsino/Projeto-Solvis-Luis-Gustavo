# Teste Técnico — Analista de Dados Pleno 2026

## Estrutura de entregáveis

```
Satisfação Solvis/
├── README.md                    ← instruções de replicação
├── rodar_tudo.bat               ← executa todos os scripts (duplo clique)
├── Q1_brief.py                  ← Q1: gera briefing executivo PDF
├── Q2_dashboard.py              ← Q2: gera dashboard NPS estático (PNG + PDF)
├── Q3_queries.py                ← Q3: queries SQL via DuckDB
├── Q4_analise.py                ← Q4: ETL + EDA + slides PDF
├── powerbi_datasource.py        ← fonte de dados do Power BI
├── dashboard_satisfacao.pbix    ← dashboard Power BI interativo
└── data/                        ← parquets (baixados automaticamente na 1ª execução)
```

Arquivos gerados na **Área de Trabalho**, em `Desktop/Teste Técnico - Luis Gustavo/`:

```
Teste Técnico - Luis Gustavo/
├── Q1_briefing.pdf              ← briefing executivo (Q1)
├── Q2_dashboard.png             ← dashboard NPS estático (Q2)
├── Q2_dashboard.pdf
├── Q4_slides.pdf                ← slides de apresentação (Q4)
├── Q4_graficos/                 ← gráficos EDA individuais (Q4)
│   ├── achado1_regiao.png
│   ├── achado2_questao.png
│   ├── achado3_ranking_lojas.png
│   ├── achado4_tendencia.png
│   └── achado5_heatmap.png
└── csv/                         ← dados para o Power BI
    ├── sat_regiao.csv
    ├── sat_questao.csv
    ├── sat_loja.csv
    ├── sat_mes.csv
    ├── sat_loja_questao.csv
    ├── nps.csv
    └── atributos.csv
```

---

## Como replicar

### Pré-requisitos

| Ferramenta | Versão mínima |
|---|---|
| Python | 3.9+ |
| Power BI Desktop | qualquer versão |

### 1. Instalar dependências Python

```bash
pip install pandas pyarrow duckdb matplotlib
```

### 2. Rodar os scripts

**Opção A — duplo clique (recomendado):**
Abrir a pasta e dar duplo clique em `rodar_tudo.bat`. Ele executa todos os scripts em sequência e mantém o terminal aberto ao final.

**Opção B — terminal:**
```bash
python Q4_analise.py   # rodar primeiro — gera os CSVs para o Power BI
python Q1_brief.py
python Q2_dashboard.py
python Q3_queries.py
```

Na primeira execução, os scripts baixam automaticamente os parquets do repositório GitHub. Não é necessário baixar nada manualmente.

### 3. Abrir o dashboard Power BI

1. Abrir `dashboard_satisfacao.pbix` no **Power BI Desktop**
2. Clicar em **Página Inicial → Atualizar**

O Power BI lê os CSVs em `Desktop/Teste Técnico - Luis Gustavo/csv/` via `powerbi_datasource.py`.

> **Nota sobre medidas DAX:** as medidas `Sat Regiao`, `Sat Loja`, `Sat Mes`, `Sat Questao` e `Sat Loja Questao` (embutidas no `.pbix`) dividem os valores por 10 para corrigir o locale pt-BR na leitura dos CSVs. Os valores exibidos são os corretos.

---

## Fonte dos dados

```
https://github.com/solvis-engineering/analytics_teste_analista_dados/tree/main/nivel_pleno
```

| Arquivo | Descrição |
|---|---|
| `answers.parquet` | 802.351 respostas |
| `evaluations.parquet` | 235.461 avaliações (24.316 duplicatas removidas no ETL) |
| `stores.parquet` | 18 lojas em 3 regiões |
| `questions.parquet` | 4 questões de satisfação |
| `choices.parquet` | 5 opções de resposta |

---

## Decisões de ETL (Q4a)

| Desafio | Decisão tomada |
|---|---|
| `answers.id` é FK para `evaluations.id`, não PK própria | Renomeado para `evaluation_id` antes do join |
| `evaluations` contém 24.316 duplicatas (mesmo id, data e loja) | `drop_duplicates(subset='id', keep='first')` |
| `choices.value` é binária (0 = negativo, 100 = positivo) | Satisfação = `AVG(value)` = % de respostas positivas |
| Datas em microssegundos (`datetime64[us]`) | Convertidas com `pd.to_datetime()` + extração de período mensal |

---

## Achados EDA (Q4b)

| # | Achado | Resultado |
|---|---|---|
| 1 | Satisfação por região | A (70,7%) ≈ B (70,6%) >> C (66,0%) |
| 2 | Atributo crítico | Preços: apenas 40,2% de satisfação — meta de 70% não atingida |
| 3 | Melhor / pior loja | LOJA 12-B (78,8%) vs LOJA 17-C (62,2%) |
| 4 | Tendência mensal | Estável Jan–Fev; Região B com queda em março |
| 5 | Padrão regional | Preços é crítico nas 3 regiões (38–41%) |

---

## Questão 3 — SQL com DuckDB

As queries foram escritas em **DuckDB**, engine SQL analítico embarcado com sintaxe compatível com PostgreSQL. A escolha garante reprodutibilidade: sem servidor, sem configuração — basta rodar `python Q3_queries.py`. As views criadas simulam o esquema de um banco PostgreSQL convencional. A query dinâmica de particionamento (Q3c) foi entregue em sintaxe PostgreSQL nativa com bloco `DO $$`, acompanhada do equivalente executável em DuckDB.
