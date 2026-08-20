"""
Dashboard NPS e Satisfacao por Atributo - 16:9
Dados: enunciado do teste (1T e 2T 2026)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# --- usuário: define a pasta de saída na Área de Trabalho ---
USUARIO = 'Luis Gustavo'
OUT_DIR = Path.home() / 'Desktop' / f'Teste Técnico - {USUARIO}'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- paleta de cores ---

COR_PROMOTOR  = '#27AE60'
COR_NEUTRO    = '#F39C12'
COR_DETRATOR  = '#E74C3C'
COR_Q1        = '#1B4F8A'
COR_Q2        = '#5DADE2'
COR_FUNDO     = '#F4F6F9'
COR_PAINEL    = '#FFFFFF'

# --- dados brutos do enunciado e cálculo do NPS ---
q1_prom, q1_neu, q1_det = 2689, 149, 147
q2_prom, q2_neu, q2_det = 2886, 166, 103

def nps(prom, neu, det):
    total = prom + neu + det
    return round((prom - det) / total * 100, 1)

nps_q1 = nps(q1_prom, q1_neu, q1_det)
nps_q2 = nps(q2_prom, q2_neu, q2_det)

atributos = ['Qualidade', 'Atendimento', 'Precos', 'Tempo de espera']
sat_q1    = [80, 82, 45, 69]
sat_q2    = [82, 82, 47, 70]

# --- estrutura da figura: cabeçalho + grid 2x3 ---
fig = plt.figure(figsize=(16, 9), facecolor=COR_FUNDO)

fig.add_artist(mpatches.Rectangle(
    (0, 0.88), 1, 0.12,
    transform=fig.transFigure,
    facecolor=COR_Q1, edgecolor='none', zorder=0))
fig.text(0.5, 0.955, 'Painel de Satisfacao de Clientes',
         ha='center', fontsize=20, fontweight='bold', color='white', zorder=1)
fig.text(0.5, 0.900, '1o e 2o Trimestre de 2026  |  NPS e Satisfacao por Atributo',
         ha='center', fontsize=11, color='white', zorder=1)

gs = gridspec.GridSpec(2, 3, figure=fig,
                       left=0.04, right=0.97,
                       top=0.85, bottom=0.07,
                       hspace=0.38, wspace=0.30)

# --- cartão KPI: NPS do 1º trimestre ---
ax_k1 = fig.add_subplot(gs[0, 0])
ax_k1.set_facecolor(COR_PAINEL)
ax_k1.set_xlim(0, 1); ax_k1.set_ylim(0, 1); ax_k1.axis('off')
ax_k1.add_patch(mpatches.FancyBboxPatch(
    (0.05, 0.05), 0.90, 0.90,
    boxstyle='round,pad=0.02', facecolor=COR_PAINEL,
    edgecolor='#CCCCCC', linewidth=1.5))
ax_k1.text(0.5, 0.82, 'NPS  |  1o Trimestre',
           ha='center', fontsize=10, color='#777777', fontweight='bold')
ax_k1.text(0.5, 0.50, f'{nps_q1}',
           ha='center', fontsize=42, color=COR_Q1, fontweight='bold')
ax_k1.text(0.5, 0.22, f'{q1_prom+q1_neu+q1_det:,} respostas',
           ha='center', fontsize=9, color='#AAAAAA')

# --- cartão KPI: NPS do 2º trimestre com variação vs 1T ---
ax_k2 = fig.add_subplot(gs[1, 0])
ax_k2.set_facecolor(COR_PAINEL)
ax_k2.set_xlim(0, 1); ax_k2.set_ylim(0, 1); ax_k2.axis('off')
ax_k2.add_patch(mpatches.FancyBboxPatch(
    (0.05, 0.05), 0.90, 0.90,
    boxstyle='round,pad=0.02', facecolor=COR_PAINEL,
    edgecolor='#CCCCCC', linewidth=1.5))
delta = nps_q2 - nps_q1
seta  = '▲' if delta >= 0 else '▼'
cor_d = COR_PROMOTOR if delta >= 0 else COR_DETRATOR
ax_k2.text(0.5, 0.82, 'NPS  |  2o Trimestre',
           ha='center', fontsize=10, color='#777777', fontweight='bold')
ax_k2.text(0.5, 0.50, f'{nps_q2}',
           ha='center', fontsize=42, color=COR_Q2, fontweight='bold')
ax_k2.text(0.5, 0.28, f'{seta} {abs(delta):.1f} pts vs 1T',
           ha='center', fontsize=10, color=cor_d, fontweight='bold')
ax_k2.text(0.5, 0.13, f'{q2_prom+q2_neu+q2_det:,} respostas',
           ha='center', fontsize=9, color='#AAAAAA')

# --- gráfico de barras empilhadas: distribuição promotores/neutros/detratores ---
ax_nps = fig.add_subplot(gs[:, 1])
ax_nps.set_facecolor(COR_PAINEL)

trimestres = ['1o Trim.', '2o Trim.']
totais     = [q1_prom+q1_neu+q1_det, q2_prom+q2_neu+q2_det]
pct_prom   = [p/t*100 for p,t in zip([q1_prom,q2_prom], totais)]
pct_neu    = [n/t*100 for n,t in zip([q1_neu, q2_neu],  totais)]
pct_det    = [d/t*100 for d,t in zip([q1_det, q2_det],  totais)]

x = np.arange(len(trimestres))
w = 0.4

b1 = ax_nps.bar(x, pct_prom, w, label='Promotores',  color=COR_PROMOTOR)
b2 = ax_nps.bar(x, pct_neu,  w, bottom=pct_prom,     label='Neutros',    color=COR_NEUTRO)
b3 = ax_nps.bar(x, pct_det,  w,
                bottom=[p+n for p,n in zip(pct_prom, pct_neu)],
                label='Detratores', color=COR_DETRATOR)

for bars, pcts, bot in [
    (b1, pct_prom, [0]*2),
    (b2, pct_neu,  pct_prom),
    (b3, pct_det,  [p+n for p,n in zip(pct_prom, pct_neu)]),
]:
    for bar, pct, b in zip(bars, pcts, bot):
        if pct > 3:
            ax_nps.text(bar.get_x() + bar.get_width()/2,
                        b + pct/2,
                        f'{pct:.1f}%',
                        ha='center', va='center',
                        fontsize=9, color='white', fontweight='bold')

ax_nps.set_xticks(x)
ax_nps.set_xticklabels(trimestres, fontsize=11)
ax_nps.set_ylabel('% de Respostas', fontsize=10)
ax_nps.set_title('Distribuicao NPS por Trimestre', fontsize=12, fontweight='bold', pad=8)
ax_nps.legend(fontsize=9, loc='upper right')
ax_nps.set_ylim(0, 115)
ax_nps.spines[['top','right']].set_visible(False)
ax_nps.set_facecolor(COR_PAINEL)

# --- gráfico de barras horizontais agrupadas: satisfação por atributo ---
ax_sat = fig.add_subplot(gs[:, 2])
ax_sat.set_facecolor(COR_PAINEL)

y     = np.arange(len(atributos))
width = 0.32

bars1 = ax_sat.barh(y + width/2, sat_q1, height=width,
                    label='1o Trim.', color=COR_Q1)
bars2 = ax_sat.barh(y - width/2, sat_q2, height=width,
                    label='2o Trim.', color=COR_Q2)

for bars, valores in [(bars1, sat_q1), (bars2, sat_q2)]:
    for bar, v in zip(bars, valores):
        ax_sat.text(v + 1.2, bar.get_y() + bar.get_height()/2,
                    f'{v}%', va='center', fontsize=9, fontweight='bold',
                    color='#333333')

ax_sat.set_yticks(y)
ax_sat.set_yticklabels(atributos, fontsize=11)
ax_sat.set_xlim(0, 110)
ax_sat.set_xlabel('Satisfacao (%)', fontsize=10)
ax_sat.set_title('Satisfacao por Atributo', fontsize=12, fontweight='bold', pad=8)
ax_sat.axvline(70, color='gray', linestyle='--', alpha=0.5,
               linewidth=1.5, label='Meta: 70%')
ax_sat.legend(fontsize=9, loc='lower right')
ax_sat.spines[['top','right']].set_visible(False)
ax_sat.set_facecolor(COR_PAINEL)

ax_sat.annotate('Ponto critico!',
                xy=(47, 0), xytext=(65, 0.4),
                fontsize=8, color=COR_DETRATOR, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=COR_DETRATOR, lw=1.2))

# --- rodapé e exportação em PNG e PDF ---
fig.text(0.5, 0.013,
         'Fonte: Sistema de Pesquisa de Satisfacao de Clientes | 2026',
         ha='center', fontsize=8, color='#AAAAAA')

OUT_PNG = OUT_DIR / 'Q2_dashboard.png'
OUT_PDF = OUT_DIR / 'Q2_dashboard.pdf'
fig.savefig(OUT_PNG, dpi=150, bbox_inches='tight', facecolor=COR_FUNDO)
fig.savefig(OUT_PDF,          bbox_inches='tight', facecolor=COR_FUNDO)
plt.close(fig)

print(f"PNG: {OUT_PNG}  ({OUT_PNG.stat().st_size/1024:.0f} KB)")
print(f"PDF: {OUT_PDF}  ({OUT_PDF.stat().st_size/1024:.0f} KB)")
