"""
Fonte de dados para o Power BI — lê os CSVs pré-agregados gerados por Q4_analise.py.

Pré-requisito: rodar Q4_analise.py antes de atualizar o dashboard.
Os CSVs ficam em: Desktop/Teste Técnico - Luis Gustavo/csv/

Tabelas carregadas:
  sat_regiao       — satisfação por região (3 linhas)
  sat_questao      — satisfação por atributo (4 linhas)
  sat_loja         — satisfação por loja (18 linhas)
  sat_mes          — tendência mensal por região (9 linhas)
  sat_loja_questao — satisfação por loja × atributo (72 linhas)
  nps              — distribuição NPS por trimestre (6 linhas)
  atributos        — satisfação por atributo por trimestre (8 linhas)
"""

import pandas as pd
from pathlib import Path

# --- usuário: aponta para a pasta gerada por Q4_analise.py ---
USUARIO = 'Luis Gustavo'
CSV_DIR = Path.home() / 'Desktop' / f'Teste Técnico - {USUARIO}' / 'csv'

sat_regiao       = pd.read_csv(CSV_DIR / 'sat_regiao.csv')
sat_questao      = pd.read_csv(CSV_DIR / 'sat_questao.csv')
sat_loja         = pd.read_csv(CSV_DIR / 'sat_loja.csv')
sat_mes          = pd.read_csv(CSV_DIR / 'sat_mes.csv')
sat_loja_questao = pd.read_csv(CSV_DIR / 'sat_loja_questao.csv')
nps              = pd.read_csv(CSV_DIR / 'nps.csv')
atributos        = pd.read_csv(CSV_DIR / 'atributos.csv')
