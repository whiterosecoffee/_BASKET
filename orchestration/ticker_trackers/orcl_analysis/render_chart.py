"""Render the dated ORCL instance's growth chart; no market data retrieval."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['svg.fonttype']='none'
matplotlib.rcParams['svg.hashsalt']='orcl-dated-research-v1'

HERE=Path(__file__).resolve().parent
r=json.loads((HERE/'replay-output.json').read_text())
rows=r['annual'][1:]
values=[x['cumulative_vs_ex_gain_fy26_pct'] for x in rows]
fig, ax=plt.subplots(figsize=(10,5.8))
colors=['#2676b8','#2676b8','#d59630','#65549b']
bars=ax.bar(range(4),values,color=colors,width=.58)
bars[2].set_hatch('//')
for i,(v,row) in enumerate(zip(values,rows)):
    ax.text(i,v+6,f'+{v:.1f}%\nEPS ${row["adjusted_eps"]:.2f}',ha='center',fontsize=11)
ax.set_xticks(range(4),['May 2027\nConsensus','May 2028\nConsensus','May 2029\nModeled','May 2030\nIssuer target'])
ax.set_ylim(0,250);ax.set_ylabel('Cumulative adjusted EPS growth (%)')
ax.set_title('ORCL: earnings growth by fiscal year end',loc='left',fontsize=17,pad=20)
ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
ax.spines[['top','right']].set_visible(False)
fig.text(.08,.045,'Baseline: FY2026 $6.83 EPS excluding investment gains. Dated research: Nov 21, 2026.\nFY2029 is interpolation; FY2030 uses $21 target floor. Earnings growth is not a stock-return forecast.',fontsize=9,color='#444')
fig.subplots_adjust(bottom=.23,top=.86,left=.09,right=.96)
fig.savefig(HERE/'eps-growth.png',dpi=160)
fig.savefig(HERE/'eps-growth.svg',metadata={'Date':None})

svg=HERE/'eps-growth.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
