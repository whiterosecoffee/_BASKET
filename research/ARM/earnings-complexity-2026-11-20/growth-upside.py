"""Long-horizon target arithmetic; not a DCF, price target or probability model."""
from pathlib import Path
from datetime import date
import hashlib
import json
import csv
import io
p=Path(__file__).resolve().parent
raw=(p/'growth-upside-inputs.json').read_bytes();d=json.loads(raw)
t=d['management_target'];n=d['near_term_estimates'];z=d['sensitivity']
years=(date.fromisoformat(t['period_end'])-date.fromisoformat(d['reference_date'])).days/365.25
r={'model_version':d['model_version'],'input_sha256':hashlib.sha256(raw).hexdigest(),
 'years_to_fy31':years,'reference_price_over_fy31_adjusted_eps_reference':d['reference_price']/t['adjusted_eps_lower_reference'],
 'adjusted_eps_cagr_fy28_to_fy31_reference':(t['adjusted_eps_lower_reference']/n['adjusted_eps'])**(1/3)-1,
 'revenue_cagr_fy28_to_fy31_reference':(t['total_revenue_b']/n['revenue_b'])**(1/3)-1,
 'illustrative_cohort_growth_20pct_units_20pct_content':1.2*1.2-1,
 'scenarios':[],'classification':'conditional_target_arithmetic_not_GAAP_forecast_or_fair_value'}
for eps in z['fy31_adjusted_eps_cases']:
 for pe in z['exit_adjusted_pe_cases']:
  future=eps*pe
  for discount in z['discount_rate_cases']:
   r['scenarios'].append({'fy31_adjusted_eps':eps,'fy31_adjusted_pe':pe,'future_share_price':future,'discount_rate':discount,'discounted_future_share_price':future/(1+discount)**years,'classification':z['classification']})
assert 4 < years < 5
assert 0.42 < r['adjusted_eps_cagr_fy28_to_fy31_reference'] < 0.44
assert abs(r['illustrative_cohort_growth_20pct_units_20pct_content']-.44)<1e-10
assert len(r['scenarios'])==27
series=d['five_year_eps_series']
prev=series['actual_base']['eps']; rows=[]
for x in series['forecasts']:
 rows.append({'fiscal_year':x['fiscal_year'],'period_end':str(x['fiscal_year'])+'-03-31','adjusted_eps':x['eps'],'yoy_growth_pct':(x['eps']/prev-1)*100,'pe_at_reference_price':d['reference_price']/x['eps'],'classification':'third_party_adjusted_eps_estimate'})
 prev=x['eps']
r['five_year_eps']={'provider':series['provider'],'basis':series['basis'],'rows':rows,'cagr_fy26_to_fy31':(rows[-1]['adjusted_eps']/series['actual_base']['eps'])**(1/5)-1,'source_url':series['source_url'],'annual_panel_counts_verified':False}
assert len(rows)==5 and rows[0]['fiscal_year']==2027 and rows[-1]['fiscal_year']==2031
assert abs(rows[0]['yoy_growth_pct']-(2.28/1.77-1)*100)<1e-10
assert 0.42 < r['five_year_eps']['cagr_fy26_to_fy31'] < 0.43
buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows);(p/'EPS_FIVE_YEAR.csv').write_text(buf.getvalue())
md=['# ARM five-fiscal-year EPS expectations', '', 'Reference price: November 20, 2026 regular close $152.20. USD per share. FY26 adjusted EPS actual $1.77 is the growth baseline. The table uses one vendor series throughout.', '', '| Fiscal year ending March 31 | Adjusted EPS estimate | YoY EPS growth | P/E at $152.20 |', '|---|---:|---:|---:|']
for x in rows:md.append(f"| {x['fiscal_year']} | ${x['adjusted_eps']:.2f} | {x['yoy_growth_pct']:.1f}% | {x['pe_at_reference_price']:.1f}x |")
md += ['', f"Five-fiscal-step adjusted EPS CAGR: {r['five_year_eps']['cagr_fy26_to_fy31']:.1%}.", '', 'Basis: adjusted/normalized EPS; this is not a GAAP forecast. ChartMill displays this as an analyst forecast series. Exact annual panel counts and table timestamp were not verified. FY27 estimate-history last observation is November 14. S&P Global via Stock Analysis gives $2.27/$3.09 for FY27/FY28 versus $2.28/$3.10 here. Other aggregators differ more at distant horizons. YoY rates above are recomputed from rounded EPS, not copied vendor percentages.', '', 'The acceleration is back-loaded: roughly 29%, 36% and 34% annual EPS growth is followed by 49% and 68%. At the reference price, the adjusted multiple remains about 37x March 2029 earnings and only approaches 25x by March 2030. Those are estimates, not commitments.', '', 'Arm separately targets more than $9 adjusted EPS in FYE31; the $10.40 figure is this third-party forecast, not the issuer target and not GAAP EPS. Existing GAAP consensus-derived references are around $1.75 for March 2028 and $2.60 for March 2029 under our assumed diluted shares. No GAAP FY30/FY31 EPS forecast was independently established.', '', 'FY27 is already in progress; March 2031 is about 4.36 years from November 20, 2026. A holding period is not an earnings-payback period. EPS is not a cash distribution, and investment returns depend on valuation, execution, ownership and distributions.', '', 'Source: '+series['source_url'], 'Near-year cross-check: https://stockanalysis.com/stocks/arm/forecast/', 'Prior GAAP bridge: ASSUMPTIONS_REVIEW.md', '', 'Formulas: YoY = EPS(t)/EPS(t-1)-1; reference P/E = 152.20/EPS(t); five-step CAGR = (10.40/1.77)^(1/5)-1.', '', 'Status: sourced research forecast table; no fair-value claim, probabilities or merge authorization.']
(p/'EPS_FIVE_YEAR.md').write_text('\n'.join(md)+'\n')
(p/'growth-upside-results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'years':years,'eps_cagr':r['adjusted_eps_cagr_fy28_to_fy31_reference'],'revenue_cagr':r['revenue_cagr_fy28_to_fy31_reference'],'case_9_eps_30pe':[x for x in r['scenarios'] if x['fy31_adjusted_eps']==9 and x['fy31_adjusted_pe']==30]},indent=2))
