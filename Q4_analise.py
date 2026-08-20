"""
ETL, analise exploratoria e slides de satisfacao de clientes.
Dados: repositorio solvis-engineering/analytics_teste_analista_dados
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from pathlib import Path
import urllib.request
import warnings
warnings.filterwarnings('ignore')

# --- usuário: define a pasta de saída na Área de Trabalho ---
USUARIO  = 'Luis Gustavo'
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR  = Path.home() / 'Desktop' / f'Teste Técnico - {USUARIO}'
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / 'Q4_graficos').mkdir(exist_ok=True)

# --- download automático dos parquets se ainda não existirem ---
_REPO = 'https://raw.githubusercontent.com/solvis-engineering/analytics_teste_analista_dados/main/nivel_pleno'
_ARQUIVOS = ['answers.parquet', 'evaluations.parquet', 'stores.parquet', 'questions.parquet', 'choices.parquet']

def _baixar_dados():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    pendentes = [f for f in _ARQUIVOS if not (DATA_DIR / f).exists()]
    if not pendentes:
        return
    print(f'Baixando {len(pendentes)} arquivo(s) do repositório...')
    for nome in pendentes:
        print(f'  {nome}...', end=' ', flush=True)
        urllib.request.urlretrieve(f'{_REPO}/{nome}', DATA_DIR / nome)
        print(f'{(DATA_DIR / nome).stat().st_size / 1024 / 1024:.1f} MB')
    print('Download concluído.\n')

_baixar_dados()

COR_PRIMARIA   = '#1B4F8A'
COR_SECUNDARIA = '#2ECC71'
COR_ALERTA     = '#E74C3C'
COR_NEUTRO     = '#95A5A6'

evaluations = pd.read_parquet(DATA_DIR / 'evaluations.parquet')
answers     = pd.read_parquet(DATA_DIR / 'answers.parquet')
choices     = pd.read_parquet(DATA_DIR / 'choices.parquet')
questions   = pd.read_parquet(DATA_DIR / 'questions.parquet')
stores      = pd.read_parquet(DATA_DIR / 'stores.parquet')

print(f"Carregados: {len(evaluations):,} avaliacoes | {len(answers):,} respostas")

# answers.id é FK para evaluations.id; evaluations tem 24.316 duplicatas por id — manter o primeiro
n_raw = len(evaluations)
evaluations = evaluations.drop_duplicates(subset='id', keep='first')
print(f"Duplicatas removidas de evaluations: {n_raw - len(evaluations):,} linhas")

answers_r     = answers.rename(columns={'id': 'evaluation_id'})
evaluations_r = evaluations.rename(columns={'id': 'evaluation_id'})
stores_r      = stores.rename(columns={'id': 'store_id', 'name': 'store_name'})
choices_r     = choices.rename(columns={'id': 'choice_id', 'name': 'choice_name'})
questions_r   = questions.rename(columns={'id': 'question_id', 'name': 'question_name'})

df = (
    answers_r
    .merge(evaluations_r, on='evaluation_id')
    .merge(stores_r,      on='store_id')
    .merge(choices_r,     on='choice_id')
    .merge(questions_r,   on='question_id')
)

# choices.value binaria: 0=negativo, 100=positivo
df['satisfeito'] = (df['value'] == 100).astype(int)

df['date_time'] = pd.to_datetime(df['date_time'])
df['mes']       = df['date_time'].dt.to_period('M').astype(str)
df['data']      = df['date_time'].dt.date

n_ev_unique = evaluations['id'].nunique()
n_df_unique = df['evaluation_id'].nunique()
assert n_df_unique <= n_ev_unique, "Mais avaliacoes no df do que na fonte"
print(f"Avaliacoes com respostas: {n_df_unique:,} de {n_ev_unique:,} ({n_df_unique/n_ev_unique*100:.1f}%)")
assert df['region'].nunique() == 3, "Regioes inesperadas"
assert df['question_name'].nunique() == 4, "Questoes inesperadas"
assert df['value'].isin([0.0, 100.0]).all(), "Valores de choice fora do esperado"

print(f"DataFrame analitico: {df.shape}")
print(f"  Periodo: {df['date_time'].min().date()} -> {df['date_time'].max().date()}")
print(f"  Avaliacoes unicas: {df['evaluation_id'].nunique():,}")
print(f"  Regioes: {sorted(df['region'].unique())}")
print(f"  Questoes: {sorted(df['question_name'].unique())}")

sat_regiao = (
    df.groupby('region')['satisfeito']
    .mean()
    .mul(100)
    .round(1)
    .sort_values(ascending=False)
    .reset_index()
    .rename(columns={'satisfeito': 'satisfacao_pct'})
)
print("\nSatisfacao geral por regiao (%)")
print(sat_regiao.to_string(index=False))

fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.bar(sat_regiao['region'], sat_regiao['satisfacao_pct'],
              color=COR_PRIMARIA, width=0.5)
ax.bar_label(bars, fmt='%.1f%%', padding=3, fontsize=11, fontweight='bold')
ax.set_ylim(0, 110)
ax.set_xlabel('Regiao', fontsize=12)
ax.set_ylabel('Satisfacao (%)', fontsize=12)
ax.set_title('Satisfacao Geral por Regiao', fontsize=13, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'Q4_graficos' / 'achado1_regiao.png', dpi=150)
plt.close(fig)

sat_questao = (
    df.groupby('question_name')['satisfeito']
    .mean()
    .mul(100)
    .round(1)
    .sort_values(ascending=True)
    .reset_index()
    .rename(columns={'satisfeito': 'satisfacao_pct'})
)
print("\nSatisfacao por questao (%)")
print(sat_questao.to_string(index=False))

cores_barra = [COR_ALERTA if v < 70 else COR_PRIMARIA for v in sat_questao['satisfacao_pct']]
fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.barh(sat_questao['question_name'], sat_questao['satisfacao_pct'],
               color=cores_barra, height=0.5)
ax.bar_label(bars, fmt='%.1f%%', padding=3, fontsize=11, fontweight='bold')
ax.set_xlim(0, 115)
ax.set_xlabel('Satisfacao (%)', fontsize=12)
ax.set_title('Satisfacao por Atributo', fontsize=13, fontweight='bold')
ax.axvline(70, color='gray', linestyle='--', alpha=0.5, label='Meta 70%')
ax.legend(fontsize=10)
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'Q4_graficos' / 'achado2_questao.png', dpi=150)
plt.close(fig)

sat_loja = (
    df.groupby(['region', 'store_name'])['satisfeito']
    .mean()
    .mul(100)
    .round(1)
    .reset_index()
    .rename(columns={'satisfeito': 'satisfacao_pct'})
    .sort_values('satisfacao_pct', ascending=False)
)
top5    = sat_loja.head(5)
bottom5 = sat_loja.tail(5).sort_values('satisfacao_pct')
print("\nTop 5 lojas")
print(top5.to_string(index=False))
print("Bottom 5 lojas")
print(bottom5.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, dados, titulo, cor in [
    (axes[0], top5,    'Top 5 Lojas',    COR_SECUNDARIO := COR_SECUNDARIA),
    (axes[1], bottom5, 'Bottom 5 Lojas', COR_ALERTA),
]:
    labels = dados['store_name'] + ' (' + dados['region'] + ')'
    bars = ax.barh(labels, dados['satisfacao_pct'], color=cor, height=0.5)
    ax.bar_label(bars, fmt='%.1f%%', padding=3, fontsize=10, fontweight='bold')
    ax.set_xlim(0, 115)
    ax.set_title(titulo, fontsize=12, fontweight='bold')
    ax.spines[['top', 'right']].set_visible(False)
fig.suptitle('Ranking de Lojas por Satisfacao', fontsize=13, fontweight='bold')
fig.tight_layout()
fig.savefig(OUT_DIR / 'Q4_graficos' / 'achado3_ranking_lojas.png', dpi=150)
plt.close(fig)

sat_mes = (
    df.groupby(['mes', 'region'])['satisfeito']
    .mean()
    .mul(100)
    .round(1)
    .reset_index()
    .rename(columns={'satisfeito': 'satisfacao_pct'})
)
print("\nTendencia mensal por regiao")
print(sat_mes.to_string(index=False))

cores_regiao = {'A': COR_PRIMARIA, 'B': COR_SECUNDARIA, 'C': COR_ALERTA}
fig, ax = plt.subplots(figsize=(8, 4))
for region, grupo in sat_mes.groupby('region'):
    ax.plot(grupo['mes'], grupo['satisfacao_pct'],
            marker='o', label=f'Regiao {region}',
            color=cores_regiao[region], linewidth=2)
ax.set_xlabel('Mes', fontsize=12)
ax.set_ylabel('Satisfacao (%)', fontsize=12)
ax.set_title('Tendencia Mensal por Regiao', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'Q4_graficos' / 'achado4_tendencia.png', dpi=150)
plt.close(fig)

pivot = (
    df.groupby(['region', 'question_name'])['satisfeito']
    .mean()
    .mul(100)
    .round(1)
    .unstack('question_name')
)
print("\nSatisfacao por questao x regiao (%)")
print(pivot.to_string())

fig, ax = plt.subplots(figsize=(9, 3.5))
im = ax.imshow(pivot.values, cmap='RdYlGn', vmin=50, vmax=100, aspect='auto')
plt.colorbar(im, ax=ax, label='Satisfacao (%)')
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns, rotation=20, ha='right', fontsize=10)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels([f'Regiao {r}' for r in pivot.index], fontsize=11)
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        ax.text(j, i, f"{pivot.values[i, j]:.1f}%",
                ha='center', va='center', fontsize=11, fontweight='bold')
ax.set_title('Satisfacao por Atributo e Regiao (%)', fontsize=13, fontweight='bold')
fig.tight_layout()
fig.savefig(OUT_DIR / 'Q4_graficos' / 'achado5_heatmap.png', dpi=150)
plt.close(fig)

W, H      = 16, 9
PDF_PATH  = OUT_DIR / 'Q4_slides.pdf'

def slide_base(fig):
    fig.patch.set_facecolor('white')
    fig.text(0.98, 0.02, 'Confidencial | Uso Interno',
             ha='right', va='bottom', fontsize=7, color='#AAAAAA')
    fig.text(0.02, 0.02, '2026',
             ha='left', va='bottom', fontsize=7, color='#AAAAAA')

with PdfPages(PDF_PATH) as pdf:

    fig = plt.figure(figsize=(W, H))
    slide_base(fig)
    ax_header = fig.add_axes([0, 0.55, 1, 0.45])
    ax_header.set_facecolor(COR_PRIMARIA)
    ax_header.axis('off')
    fig.text(0.5, 0.75, 'Analise de Satisfacao de Clientes',
             ha='center', va='center', fontsize=28, fontweight='bold', color='white')
    fig.text(0.5, 0.65, 'Resultados Consolidados -- Jan a Mar 2026',
             ha='center', va='center', fontsize=16, color='#D6E4F0')
    fig.text(0.5, 0.40, f'{len(evaluations):,} avaliacoes coletadas em 18 lojas | 3 regioes | 4 atributos',
             ha='center', va='center', fontsize=13, color='#555555')
    fig.text(0.5, 0.30, 'Analise Exploratoria de Dados',
             ha='center', va='center', fontsize=11, color='#888888')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    fig = plt.figure(figsize=(W, H))
    slide_base(fig)
    fig.text(0.05, 0.90, 'Satisfacao Geral por Regiao',
             fontsize=18, fontweight='bold', color=COR_PRIMARIA)
    fig.text(0.05, 0.83,
             'A Regiao C lidera a satisfacao, enquanto a Regiao A apresenta o maior espaco de melhoria.',
             fontsize=12, color='#444444')
    ax = fig.add_axes([0.08, 0.12, 0.88, 0.65])
    cor_bars = [COR_SECUNDARIA if v == sat_regiao['satisfacao_pct'].max()
                else COR_PRIMARIA for v in sat_regiao['satisfacao_pct']]
    bars = ax.bar(sat_regiao['region'], sat_regiao['satisfacao_pct'],
                  color=cor_bars, width=0.4)
    ax.bar_label(bars, fmt='%.1f%%', padding=5, fontsize=16, fontweight='bold')
    ax.set_ylim(0, 115)
    ax.set_ylabel('% Clientes Satisfeitos', fontsize=12)
    ax.set_xlabel('Regiao', fontsize=12)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=13)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    fig = plt.figure(figsize=(W, H))
    slide_base(fig)
    fig.text(0.05, 0.90, 'Precos e o Atributo Critico',
             fontsize=18, fontweight='bold', color=COR_PRIMARIA)
    fig.text(0.05, 0.83,
             'Precos concentra a maior insatisfacao. Os demais atributos estao acima de 70%.',
             fontsize=12, color='#444444')
    ax = fig.add_axes([0.08, 0.12, 0.88, 0.65])
    cores_b = [COR_ALERTA if v < 70 else COR_PRIMARIA for v in sat_questao['satisfacao_pct']]
    bars = ax.barh(sat_questao['question_name'], sat_questao['satisfacao_pct'],
                   color=cores_b, height=0.45)
    ax.bar_label(bars, fmt='%.1f%%', padding=5, fontsize=14, fontweight='bold')
    ax.set_xlim(0, 115)
    ax.axvline(70, color='gray', linestyle='--', alpha=0.6, linewidth=1.5, label='Meta minima: 70%')
    ax.legend(fontsize=11)
    ax.set_xlabel('% Clientes Satisfeitos', fontsize=12)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=13)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    fig = plt.figure(figsize=(W, H))
    slide_base(fig)
    fig.text(0.05, 0.90, 'Precos e critico em todas as regioes',
             fontsize=18, fontweight='bold', color=COR_PRIMARIA)
    fig.text(0.05, 0.83,
             'O padrao de baixa satisfacao com Precos e consistente nas tres regioes.',
             fontsize=12, color='#444444')
    ax = fig.add_axes([0.08, 0.10, 0.82, 0.68])
    im = ax.imshow(pivot.values, cmap='RdYlGn', vmin=50, vmax=100, aspect='auto')
    plt.colorbar(im, ax=ax, label='% Satisfacao', shrink=0.8)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=13)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([f'Regiao {r}' for r in pivot.index], fontsize=13)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            ax.text(j, i, f"{pivot.values[i, j]:.1f}%",
                    ha='center', va='center', fontsize=14, fontweight='bold')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    fig = plt.figure(figsize=(W, H))
    slide_base(fig)
    fig.text(0.05, 0.90, 'Tendencia e Destaques',
             fontsize=18, fontweight='bold', color=COR_PRIMARIA)
    fig.text(0.05, 0.83,
             'Satisfacao estavel no periodo. Identifique as lojas referencia e as que precisam de acao.',
             fontsize=12, color='#444444')

    gs = gridspec.GridSpec(1, 2, figure=fig, left=0.06, right=0.96,
                           bottom=0.12, top=0.78, wspace=0.3)

    ax1 = fig.add_subplot(gs[0])
    for region, grupo in sat_mes.groupby('region'):
        ax1.plot(grupo['mes'], grupo['satisfacao_pct'],
                 marker='o', label=f'Regiao {region}',
                 color=cores_regiao[region], linewidth=2.5)
    ax1.set_title('Tendencia Mensal', fontsize=12, fontweight='bold')
    ax1.set_ylabel('% Satisfacao', fontsize=10)
    ax1.legend(fontsize=9)
    ax1.spines[['top', 'right']].set_visible(False)
    ax1.tick_params(axis='x', rotation=20)

    ax2 = fig.add_subplot(gs[1])
    top3    = sat_loja.head(3)
    bottom3 = sat_loja.tail(3).sort_values('satisfacao_pct')
    combined = pd.concat([bottom3, top3])
    cores_combined = [COR_ALERTA] * 3 + [COR_SECUNDARIA] * 3
    labels = combined['store_name'] + ' (' + combined['region'] + ')'
    bars = ax2.barh(labels, combined['satisfacao_pct'],
                    color=cores_combined, height=0.5)
    ax2.bar_label(bars, fmt='%.1f%%', padding=3, fontsize=10, fontweight='bold')
    ax2.set_xlim(0, 115)
    ax2.set_title('Top 3 e Bottom 3 Lojas', fontsize=12, fontweight='bold')
    ax2.spines[['top', 'right']].set_visible(False)

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

print(f"Slides salvos: {PDF_PATH}  ({PDF_PATH.stat().st_size / 1024:.0f} KB)")

CSV_DIR = OUT_DIR / 'csv'
CSV_DIR.mkdir(exist_ok=True)

sat_regiao.to_csv(CSV_DIR / 'sat_regiao.csv', index=False)

sat_questao.to_csv(CSV_DIR / 'sat_questao.csv', index=False)

sat_loja.to_csv(CSV_DIR / 'sat_loja.csv', index=False)

sat_mes.to_csv(CSV_DIR / 'sat_mes.csv', index=False)

sat_loja_questao = (
    df.groupby(['region', 'store_name', 'question_name'])['satisfeito']
    .mean().mul(100).round(1).reset_index()
    .rename(columns={'satisfeito': 'satisfacao_pct'})
)
sat_loja_questao.to_csv(CSV_DIR / 'sat_loja_questao.csv', index=False)

nps_df = pd.DataFrame({
    'trimestre': ['1T 2026', '1T 2026', '1T 2026', '2T 2026', '2T 2026', '2T 2026'],
    'categoria': ['Promotores', 'Neutros', 'Detratores',
                  'Promotores', 'Neutros', 'Detratores'],
    'respostas': [2689, 149, 147, 2886, 166, 103],
    'ordem':     [1, 2, 3, 1, 2, 3],
})
nps_df['total']     = nps_df.groupby('trimestre')['respostas'].transform('sum')
nps_df['pct']       = (nps_df['respostas'] / nps_df['total'] * 100).round(1)
nps_df['nps_score'] = nps_df['trimestre'].map({
    '1T 2026': round((2689 - 147) / (2689 + 149 + 147) * 100, 1),
    '2T 2026': round((2886 - 103) / (2886 + 166 + 103) * 100, 1),
})
nps_df.to_csv(CSV_DIR / 'nps.csv', index=False)

atributos_df = pd.DataFrame({
    'atributo':       ['Qualidade', 'Atendimento', 'Precos', 'Tempo de espera'] * 2,
    'trimestre':      ['1T 2026'] * 4 + ['2T 2026'] * 4,
    'satisfacao_pct': [80, 82, 45, 69, 82, 82, 47, 70],
    'meta_pct':       [70] * 8,
})
atributos_df['acima_meta'] = atributos_df['satisfacao_pct'] >= atributos_df['meta_pct']
atributos_df['variacao']   = atributos_df.groupby('atributo')['satisfacao_pct'].diff().fillna(0)
atributos_df.to_csv(CSV_DIR / 'atributos.csv', index=False)

for f in sorted(CSV_DIR.glob('*.csv')):
    rows = sum(1 for _ in open(f)) - 1
    print(f"  {f.name:<30} {rows} linhas")

print(f"\nCSVs prontos em: {CSV_DIR}")
