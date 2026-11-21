"""Research arithmetic replay, not a valuation engine or provider adapter."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

VERSION = 'company-analysis-method/0.1.0-draft'

def finite(x, name, positive=False):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise ValueError(f'{name}: finite number required')
    if positive and x <= 0:
        raise ValueError(f'{name}: must be positive')
    return x

def pe(price, eps):
    return price / eps if eps > 0 else None

def build(instance):
    raw = (instance / 'inputs.json').read_bytes()
    data = json.loads(raw)
    sources = json.loads((instance / 'sources.json').read_text())
    ids = [s['id'] for s in sources['records']]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate source id')
    def refs(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key.endswith('source_ids'):
                    if not set(value) <= set(ids):
                        raise ValueError('unresolved sources')
                else:
                    refs(value)
        elif isinstance(obj, list):
            for value in obj:
                refs(value)
    refs(data)
    p = finite(data['price_reference']['value'], 'price', True)
    baseline = finite(data['baseline']['adjusted_ex_investment_gains_eps'], 'baseline', True)
    reported = finite(data['baseline']['adjusted_eps'], 'reported', True)
    rows = data['eps_series']
    years = [r['fiscal_year'] for r in rows]
    if years != sorted(set(years)):
        raise ValueError('years must be unique and sorted')
    values = []
    for i, row in enumerate(rows):
        eps = row['eps']
        if row['classification'] == 'modeled_interpolation':
            if eps is not None or i == 0 or i == len(rows)-1:
                raise ValueError('interpolation must remain explicitly modeled')
            eps = math.sqrt(values[-1] * finite(rows[i+1]['eps'], 'endpoint', True))
        values.append(finite(eps, 'eps'))
    first_forward = values[1]
    result = {'method_version':VERSION, 'input_sha256':hashlib.sha256(raw).hexdigest(),
              'ticker':data['ticker'], 'as_of':data['as_of'],
              'price_status':data['price_reference']['status'], 'current_quote_eligible':False,
              'annual':[], 'scenarios':[], 'checks':[]}
    prior = data['baseline']['prior_adjusted_eps']
    for row, eps in zip(rows, values):
        result['annual'].append({'fiscal_year':row['fiscal_year'],'period_end':row['period_end'],
            'classification':row['classification'],'adjusted_eps':eps, 'gaap_eps':row['gaap_eps'],
            'yoy_pct':(eps/prior-1)*100 if prior > 0 else None,
            'cumulative_vs_ex_gain_fy26_pct':(eps/baseline-1)*100 if row['fiscal_year'] > data['baseline']['fiscal_year'] else None,
            'cumulative_vs_reported_fy26_pct':(eps/reported-1)*100,
            'cumulative_vs_first_forward_pct':(eps/first_forward-1)*100,
            'historical_reference_pe':pe(p,eps),
            'price_equivalent_at_first_forward_pe':eps*p/first_forward if eps > 0 else None,
            'illustrative_prices':{str(m):eps*m if eps > 0 else None for m in data['multiples']}})
        prior = eps
    for sc in data['scenarios']:
        rev = finite(sc['revenue_usd_b'],'revenue',True)
        margin = finite(sc['adjusted_operating_margin'],'margin')
        tax = finite(sc['tax_rate'],'tax')
        if not 0 <= tax <= 1 or not 0 <= margin <= 1:
            raise ValueError('invalid fraction')
        cost = finite(sc['net_nonoperating_cost_usd_b'],'net cost')
        shares = finite(sc['diluted_shares_b'],'shares',True)
        preferred = finite(sc['preferred_dividends_usd_b'],'preferred')
        if preferred < 0:
            raise ValueError('negative preferred distributions')
        pretax = rev*margin-cost
        net = pretax-max(pretax,0)*tax-preferred
        eps = net/shares
        result['scenarios'].append({'name':sc['name'],'classification':'scenario','net_common_income_usd_b':net,'eps':eps,
            'historical_reference_pe':pe(p,eps),'price_at_15x':eps*15 if eps > 0 else None})
    f = data['financing']
    issued = f['common_shares_aug31']+f['november_common_shares']
    conversion = [f['preferred_shares']*f[key] for key in ('conversion_per_preferred_min','conversion_per_preferred_max')]
    coupon = sum(n['principal_usd_b']*n['coupon'] for n in data['november_notes'])
    principal = sum(n['principal_usd_b'] for n in data['november_notes'])
    result['financing_arithmetic']={'proforma_common_shares':issued,'conversion_share_range':conversion,
        'proforma_after_conversion_before_other_changes':[issued+c for c in conversion],
        'new_notes_annual_coupon_usd_b':coupon,'weighted_new_coupon':coupon/principal,
        'q1_interest_annualized_plus_coupon_usd_b':f['q1_interest_expense_usd_b']*4+coupon,
        'interest_capitalized_usd_b':None,'forward_fully_diluted_shares':None}
    result['checks']=['unique source IDs and resolved input references','unique sorted fiscal years',
        'explicit interpolation classification','finite numeric and fraction guards',
        'current quote eligibility withheld','negative/nonpositive EPS does not produce positive P/E']
    return result

def validate_links(instance):
    base = instance.parent / 'analysis_method'
    for directory in (instance,base):
        state = json.loads((directory/'state.json').read_text())
        for key, value in state['files'].items():
            if not (directory/value).is_file():
                raise ValueError(f'missing {key}: {value}')
    child = json.loads((instance/'state.json').read_text())
    rows = [json.loads(line) for line in (instance/child['files']['observations']).read_text().splitlines()]
    if len({r['record_id'] for r in rows}) != len(rows):
        raise ValueError('duplicate observation id')
    if {r['ingested_at'][:10] for r in rows} != {child['as_of']}:
        raise ValueError('research log contains multiple ingestion dates')
    return len(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--instance',type=Path,required=True)
    ap.add_argument('--check-links',action='store_true')
    args=ap.parse_args()
    output=build(args.instance)
    if args.check_links:
        output['link_check_observations']=validate_links(args.instance)
    print(json.dumps(output,indent=2,allow_nan=False))

if __name__ == '__main__':
    main()
