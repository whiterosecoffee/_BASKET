"""Long-horizon target arithmetic; not a DCF, price target or probability model."""
from pathlib import Path
from datetime import date
import hashlib
import json
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
(p/'growth-upside-results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'years':years,'eps_cagr':r['adjusted_eps_cagr_fy28_to_fy31_reference'],'revenue_cagr':r['revenue_cagr_fy28_to_fy31_reference'],'case_9_eps_30pe':[x for x in r['scenarios'] if x['fy31_adjusted_eps']==9 and x['fy31_adjusted_pe']==30]},indent=2))
