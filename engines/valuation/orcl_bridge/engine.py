"""Deterministic USD valuation bridges. Outputs are conditional, never probabilities."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

VERSION = 'orcl-valuation-bridge/1.0.0'
METRICS = ('pe', 'ev_ebitda', 'ev_sales', 'price_equity_fcf', 'ev_fcff')


def timestamp(s):
    result = datetime.fromisoformat(s.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timezone required')
    return result.astimezone(timezone.utc)


def number(value, label, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(label + ': finite number required')
    if minimum is not None and value < minimum or maximum is not None and value > maximum:
        raise ValueError(label + ': out of bounds')
    return value


def ratio(a, b):
    return a / b if b > 0 and a > 0 else None


def evidence(record, at, max_age):
    """Review freshness is separate from effective period/publication vintage."""
    if record['verification'] != 'verified':
        raise ValueError('unverified input')
    if record['classification'] not in ('source_fact', 'issuer_statement', 'consensus', 'analyst_estimate'):
        raise ValueError('unsupported input class')
    for key in ('observed_at', 'available_at', 'ingested_at'):
        if timestamp(record[key]) > at:
            raise ValueError('input not known as of requested time')
    observed = timestamp(record['observed_at'])
    if at >= timestamp(record['expires_at']) or (at-observed).total_seconds() >= max_age:
        raise ValueError('stale input')
    if not record['source_id'] or not record['sources']:
        raise ValueError('missing provenance')
    for url in record['sources']:
        if urlparse(url).scheme != 'https' or not urlparse(url).netloc:
            raise ValueError('HTTPS source required')
    return record['data']


def company(record, at):
    if record['currency'] != 'USD':
        raise ValueError('inputs must be converted to USD upstream with conversion provenance')
    q = evidence(record['quote'], at, 300)
    f = evidence(record['forecast'], at, 86400)
    b = evidence(record['balance'], at, 86400)
    if timestamp(record['quote']['effective_at']) > at or timestamp(record['balance']['effective_at']) > at:
        raise ValueError('future quote or balance')
    if (at-timestamp(record['quote']['effective_at'])).total_seconds() >= 300:
        raise ValueError('stale quote effective time')
    start, end = timestamp(f['horizon_start']), timestamp(f['horizon_end'])
    if not 350 <= (end-start).days <= 380 or not (start.date() == at.date() and at < end):
        raise ValueError('forward horizon must be one aligned annual period containing as_of')
    if f['earnings_basis'] not in ('GAAP', 'normalized'):
        raise ValueError('explicit earnings basis required')
    if f['earnings_basis'] == 'normalized' and not f.get('reconciliation'):
        raise ValueError('normalized earnings require reconciliation')
    if f['lease_basis'] != 'included_consistent':
        raise ValueError('EV and earnings must share documented lease treatment')
    for k in ('revenue', 'da', 'capex', 'cash_interest', 'diluted_shares'):
        number(f[k], k, 0)
    if not f['revenue'] or not f['diluted_shares']:
        raise ValueError('revenue and shares must be positive')
    number(f['ebit'], 'ebit')
    number(f['delta_nwc'], 'delta_nwc')
    number(f['tax_rate'], 'tax_rate', 0, 1)
    for k in ('debt', 'cash', 'leases', 'preferred', 'minority'):
        number(b[k], k, 0)
    number(q['price'], 'price', 0)
    if not q['price']:
        raise ValueError('positive price required')
    # Cash tax shields are recognized only to the extent taxable profit exists.
    pretax = f['ebit']-f['cash_interest']
    net_income = pretax-max(pretax, 0)*f['tax_rate']
    ebitda = f['ebit']+f['da']
    fcff = f['ebit']-max(f['ebit'], 0)*f['tax_rate']+f['da']-f['capex']-f['delta_nwc']
    equity_fcf = net_income+f['da']-f['capex']-f['delta_nwc']
    # These are modeled cash flows excluding net new borrowing, not reported CFO-capex.
    net_obligations = b['debt']+b['leases']+b['preferred']+b['minority']-b['cash']
    market_cap = q['price']*f['diluted_shares']
    ev = market_cap+net_obligations
    stats = {'eps':net_income/f['diluted_shares'], 'net_income':net_income, 'ebitda':ebitda,
             'fcff':fcff, 'equity_fcf_before_net_borrowing':equity_fcf,
             'market_cap':market_cap, 'enterprise_value':ev, 'net_obligations':net_obligations,
             'operating_margin':f['ebit']/f['revenue'], 'equity_fcf_yield':equity_fcf/market_cap,
             'pe':ratio(market_cap,net_income), 'ev_ebitda':ratio(ev,ebitda),
             'ev_sales':ratio(ev,f['revenue']), 'price_equity_fcf':ratio(market_cap,equity_fcf),
             'ev_fcff':ratio(ev,fcff)}
    return {'ticker':record['ticker'], 'quote':q, 'forecast':f, 'balance':b, 'stats':stats,
            'source_ids':[record[k]['source_id'] for k in ('quote','forecast','balance')],
            'quote_time':record['quote']['effective_at']}


def weighted_median(values):
    total = sum(weight for _,weight in values)
    cumulative = 0
    for value,weight in sorted(values):
        cumulative += weight
        if cumulative >= total/2:
            return value
    raise ValueError('empty median')


def implied_price(target, metric, multiple):
    s,f = target['stats'],target['forecast']
    if metric == 'pe':
        return multiple*s['eps'] if s['eps'] > 0 else None
    if metric == 'price_equity_fcf':
        return multiple*s['equity_fcf_before_net_borrowing']/f['diluted_shares'] if s['equity_fcf_before_net_borrowing'] > 0 else None
    denominator = {'ev_ebitda':s['ebitda'], 'ev_sales':f['revenue'], 'ev_fcff':s['fcff']}[metric]
    return max(0, (multiple*denominator-s['net_obligations'])/f['diluted_shares']) if denominator > 0 else None


def compare(target, peers, weights):
    output = {}
    for metric in METRICS:
        eligible, excluded = [], []
        for ticker, weight in weights.items():
            peer = peers.get(ticker)
            why = None
            if not peer:
                why = 'missing_or_invalid_input'
            elif any(peer['forecast'][key] != target['forecast'][key] for key in ('horizon_start','horizon_end','earnings_basis','lease_basis')):
                why = 'incomparable_horizon_or_basis'
            elif abs((timestamp(peer['quote_time'])-timestamp(target['quote_time'])).total_seconds()) > 120:
                why = 'unaligned_quotes'
            elif peer['stats'][metric] is None:
                why = 'nonpositive_denominator_or_EV'
            if why:
                excluded.append({'ticker':ticker,'reason':why,'weight':weight})
            else:
                eligible.append((peer['stats'][metric],weight))
        coverage = sum(w for _,w in eligible)
        # No silent renormalization. A partial median is explicitly provisional.
        median = weighted_median(eligible) if eligible else None
        current = target['stats'][metric]
        full = math.isclose(coverage,1.0,abs_tol=1e-9)
        price = implied_price(target,metric,median) if median is not None and full else None
        output[metric] = {'target_multiple':current, 'peer_weight_coverage':coverage,
                          'peer_median':median, 'peer_mean':sum(v*w for v,w in eligible)/coverage if coverage else None,
                          'status':'complete' if full else 'partial_non_actionable', 'excluded':excluded,
                          'relative_ratio':current/median if current is not None and median else None,
                          'implied_price_usd':price,
                          'implied_upside_fraction':price/target['quote']['price']-1 if price is not None else None}
    return output


def scenario(target, spec):
    """Annual forward earnings scenario; all changes incremental to forecast."""
    if not spec.get('rationale') or not spec.get('falsifiers'):
        raise ValueError('scenario rationale and falsifiers required')
    f,b = target['forecast'],target['balance']
    for k in ('revenue_change','margin_change','capex_change','delta_nwc_change'):
        number(spec[k],k)
    for k in ('new_debt','equity_raise','additional_shares','retained_funding_cash'):
        number(spec[k],k,0)
    number(spec['new_debt_rate'],'new_debt_rate',0,1)
    number(spec['new_debt_year_fraction'],'new_debt_year_fraction',0,1)
    number(spec['issue_price'],'issue_price',0)
    number(spec['da_change'],'da_change')
    if spec['equity_raise'] and not spec['issue_price']:
        raise ValueError('equity raise requires positive issue price')
    if spec['retained_funding_cash'] > spec['new_debt']+spec['equity_raise']:
        raise ValueError('retained funding exceeds proceeds')
    interest_delta = 0
    repriced_principal = 0
    lines = []
    seen_tranches = set()
    for tranche in spec['repricing']:
        if not tranche['tranche_id'] or tranche['tranche_id'] in seen_tranches:
            raise ValueError('unique debt tranche IDs required')
        seen_tranches.add(tranche['tranche_id'])
        kind = tranche['kind']
        if kind not in ('fixed','floating','refinancing'):
            raise ValueError('invalid debt category')
        principal = number(tranche['principal'],'principal',0)
        old = number(tranche['old_rate'],'old_rate',0,1)
        new = number(tranche['new_rate'],'new_rate',0,1)
        fraction = number(tranche['year_fraction'],'year_fraction',0,1)
        if kind == 'fixed' and new != old:
            raise ValueError('fixed debt does not reprice without refinancing')
        repriced_principal += principal
        delta = principal*(new-old)*fraction
        interest_delta += delta
        lines.append({'kind':kind,'interest_change_usd':delta})
    if repriced_principal > b['debt']:
        raise ValueError('tranches exceed existing debt; partition without overlap')
    interest_delta += spec['new_debt']*spec['new_debt_rate']*spec['new_debt_year_fraction']
    interest = f['cash_interest']+interest_delta
    if interest < 0:
        raise ValueError('negative modeled interest expense')
    revenue = f['revenue']*(1+spec['revenue_change'])
    margin = target['stats']['operating_margin']+spec['margin_change']
    if revenue <= 0 or margin > 1 or margin < -1:
        raise ValueError('invalid revenue/margin scenario')
    shares = f['diluted_shares']+spec['additional_shares']+(spec['equity_raise']/spec['issue_price'] if spec['equity_raise'] else 0)
    ebit = revenue*margin
    pretax = ebit-interest
    net_income = pretax-max(pretax,0)*f['tax_rate']
    da,capex,nwc = f['da']+spec['da_change'],f['capex']+spec['capex_change'],f['delta_nwc']+spec['delta_nwc_change']
    if min(da,capex) < 0:
        raise ValueError('negative D&A or capex')
    ebitda = ebit+da
    equity_fcf = net_income+da-capex-nwc
    fcff = ebit-max(ebit,0)*f['tax_rate']+da-capex-nwc
    obligations = target['stats']['net_obligations']+spec['new_debt']-spec['retained_funding_cash']
    derived = {'quote':target['quote'],'forecast':dict(f,revenue=revenue,diluted_shares=shares),
               'stats':{'eps':net_income/shares,'ebitda':ebitda,'fcff':fcff,
                        'equity_fcf_before_net_borrowing':equity_fcf,'net_obligations':obligations}}
    prices = {}
    if set(spec['multiples']) != set(METRICS):
        raise ValueError('declare every valuation multiple or null')
    for metric,multiple in spec['multiples'].items():
        if multiple is not None:
            number(multiple,metric,0)
            if not multiple:
                raise ValueError('positive multiple required')
        price = implied_price(derived,metric,multiple) if multiple else None
        prices[metric] = {'price_usd':price,'upside_fraction':price/target['quote']['price']-1 if price is not None else None}
    eps = net_income/shares
    # Exact two-step attribution: earnings change at old shares, then dilution.
    old_eps = target['stats']['eps']
    earnings_eps_delta = (net_income-target['stats']['net_income'])/f['diluted_shares']
    return {'classification':'scenario', 'rationale':spec['rationale'], 'falsifiers':spec['falsifiers'],
            'eps':eps,'eps_change':eps-old_eps,'earnings_eps_change':earnings_eps_delta,
            'dilution_eps_change':eps-(old_eps+earnings_eps_delta), 'diluted_shares':shares,
            'interest_change_usd':interest_delta,'repricing':lines,'net_obligations':obligations,
            'modeled_equity_fcf_before_net_borrowing':equity_fcf,'modeled_fcff':fcff,
            'cash_flow_warning':'Growth capex remains included; customer funding is not free cash flow.',
            'implied_prices':prices}


def rate_sensitivity(target, base):
    """Mechanical +/-100bp curve; no causal attribution to a market price move."""
    reference = scenario(target, base)
    exposure = base['new_debt']*base['new_debt_year_fraction'] + sum(
        t['principal']*t['year_fraction'] for t in base['repricing'] if t['kind'] != 'fixed')
    if exposure == 0:
        return {'status':'no_declared_repricing_exposure','rows':[]}
    rows = []
    for bps in (-100, -50, 0, 50, 100):
        shocked = copy.deepcopy(base)
        shift = bps/10000
        valid = True
        if shocked['new_debt']:
            shocked['new_debt_rate'] += shift
            valid = 0 <= shocked['new_debt_rate'] <= 1
        for t in shocked['repricing']:
            if t['kind'] != 'fixed':
                t['new_rate'] += shift
                valid = valid and 0 <= t['new_rate'] <= 1
        if not valid:
            rows.append({'shock_bps':bps,'status':'outside_rate_bounds'})
            continue
        output = scenario(target, shocked)
        rows.append({'shock_bps':bps,'incremental_interest_usd':output['interest_change_usd']-reference['interest_change_usd'],
                     'eps_delta_vs_base':output['eps']-reference['eps'],
                     'pe_implied_price_usd':output['implied_prices']['pe']['price_usd']})
    return {'status':'conditional','annualized_exposure_usd':exposure,'rows':rows}


def evaluate(bundle, as_of):
    at = timestamp(as_of)
    json.dumps(bundle,allow_nan=False)
    if bundle.get('data_mode') not in ('synthetic', 'source_backed'):
        raise ValueError('explicit data_mode required')
    if bundle['schema'] != 'basket.valuation_input@1':
        raise ValueError('unsupported schema')
    weights = bundle['peer_weights']
    if not weights or not math.isclose(sum(number(w,'peer_weight',0,1) for w in weights.values()),1,abs_tol=1e-9) or any(w==0 for w in weights.values()):
        raise ValueError('positive peer weights must sum to one')
    if bundle['target'] in weights:
        raise ValueError('target cannot be its own peer')
    report = {'schema':'basket.valuation_output@1','engine_version':VERSION,'as_of':at.isoformat(),
              'input_sha256':hashlib.sha256(json.dumps(bundle,sort_keys=True,allow_nan=False).encode()).hexdigest(),
              'classification':'conditional_valuation_not_forecast','currency':'USD','data_mode':bundle['data_mode'],'gaps':[],
              'target':None,'comparisons':{},'scenarios':{},'reverse':{},'eligible':False}
    companies = {}
    for ticker in [bundle['target'],*weights]:
        try:
            record = bundle['companies'][ticker]
            if record['ticker'] != ticker:
                raise ValueError('ticker mismatch')
            companies[ticker] = company(record,at)
        except (KeyError,ValueError,TypeError) as exc:
            report['gaps'].append({'ticker':ticker,'reason':str(exc)})
    target = companies.get(bundle['target'])
    if target is None:
        return report
    report['target'] = target
    report['comparisons'] = compare(target,companies,weights)
    for metric,row in report['comparisons'].items():
        if row['status'] != 'complete':
            report['gaps'].append({'metric':metric,'reason':'incomplete comparable peer coverage'})
    report['eligible'] = not report['gaps'] and bundle['data_mode']=='source_backed'
    for name in ('bear','base','bull'):
        try:
            report['scenarios'][name] = scenario(target,bundle['scenarios'][name])
        except (KeyError,ValueError,TypeError) as exc:
            report['scenarios'][name] = {'status':'blocked','reason':str(exc)}
    try:
        report['rate_sensitivity'] = rate_sensitivity(target,bundle['scenarios']['base'])
    except (KeyError,ValueError,TypeError) as exc:
        report['rate_sensitivity'] = {'status':'blocked','reason':str(exc)}
    p = report['comparisons']['pe']
    ev = report['comparisons']['ev_ebitda']
    if p['status']=='complete':
        required = target['quote']['price']/p['peer_median']
        report['reverse']['required_eps_at_peer_pe'] = required
        report['reverse']['eps_gap_to_forecast'] = required-target['stats']['eps']
    if ev['status']=='complete':
        margin = target['stats']['enterprise_value']/(ev['peer_median']*target['forecast']['revenue'])
        report['reverse']['required_ebitda_margin_at_peer_multiple'] = margin
        report['reverse']['ebitda_margin_gap_to_forecast'] = margin-target['stats']['ebitda']/target['forecast']['revenue']
    if any(row.get('status') == 'blocked' for row in report['scenarios'].values()):
        report['eligible'] = False
    report['limits'] = ['Peer multiples are reference assumptions, not intrinsic value.',
                        'No fitted return forecast, probabilities, terminal DCF or automatic ranking.',
                        'Cash flow is modeled from annual EBIT, D&A, capex and working capital; reconcile with actual CFO upstream.',
                        'Financing and equity changes are incremental to the supplied forecast, not already included guidance.',
                        'Values are current forward-multiple indications, not future dated price targets.']
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--as-of',required=True)
    args = parser.parse_args()
    print(json.dumps(evaluate(json.loads(args.input.read_text()),args.as_of),indent=2,allow_nan=False))


if __name__=='__main__':
    main()
