"""Conditional GAAP EPS bridge. USD millions and millions of diluted shares.

Run with --check for accounting invariants, historical reconciliation and replay.
No live data, investment recommendation, vesting forecast or probabilities.
"""
from pathlib import Path
import csv
import hashlib
import io
import json
import math
import sys

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'gaap-inputs.json'


def operating_exclusions(v):
    return sum(v[k] for k in ('sbc', 'employer_tax', 'acquisition', 'other_operating'))


def calculate(d, shield=None):
    a = d['assumptions']
    shield = a['marginal_tax_shield'] if shield is None else shield
    assert 0 <= shield < 1
    h = d['historical']['H1_FY27']
    q = d['historical']['Q2_FY27']
    h_operating = sum(h[k] for k in ('sbc_restored', 'employer_tax_restored',
                                    'acquisition_restored', 'other_operating_restored'))
    h_calc = h['adjusted_net_income'] - h_operating + h['equity_gain_retained'] + h['tax_reconciliation_addback']
    q_calc = q['adjusted_net_income'] - q['sbc_restored'] - q['employer_tax_restored'] - q['acquisition_restored'] - q['equity_loss_restored'] + q['tax_reconciliation_addback']
    out = {'model_version': d['model_version'], 'reference_price': a['reference_price'],
           'marginal_tax_shield': shield,
           'historical_reconciliations': {'H1_FY27': {'calculated_gaap_ni': h_calc, 'reported_gaap_ni': h['gaap_net_income'], 'residual': h_calc-h['gaap_net_income']},
                                        'Q2_FY27': {'calculated_gaap_ni': q_calc, 'reported_gaap_ni': q['gaap_net_income'], 'residual': q_calc-q['gaap_net_income']}},
           'scenarios': []}
    for scenario in d['scenario_inputs']:
        item = {'id': scenario['id'], 'label': scenario['label'], 'classification': scenario['classification'], 'years': {}}
        for year in ('FY27', 'FY28'):
            f = d['forecast_anchors'][year]
            c = scenario[year]
            shares = f['diluted_shares_assumed']
            adjusted_ni = f['adjusted_eps'] * shares
            exclusions = operating_exclusions(c)
            if year == 'FY27':
                future_adjusted_ni = adjusted_ni - h['adjusted_net_income']
                future_exclusions = exclusions - h_operating
                if future_exclusions < 0:
                    raise ValueError('Forecast full-year costs cannot be below already expensed H1 costs')
                future_after_tax_charge = (future_exclusions + c['extra_development']) * (1-shield)
                gaap_ni = h['gaap_net_income'] + future_adjusted_ni - future_after_tax_charge
            else:
                future_adjusted_ni = adjusted_ni
                future_exclusions = exclusions
                future_after_tax_charge = (exclusions+c['extra_development']) * (1-shield)
                gaap_ni = adjusted_ni - future_after_tax_charge
            gaap_eps = gaap_ni / shares
            item['years'][year] = {'period_end': f['period_end'], 'adjusted_eps_anchor': f['adjusted_eps'],
                'diluted_shares': shares, 'adjusted_ni_anchor': adjusted_ni,
                'historical_gaap_ni_retained': h['gaap_net_income'] if year == 'FY27' else 0,
                'future_adjusted_ni': future_adjusted_ni, 'full_year_restored_expenses': exclusions,
                'future_restored_expenses': future_exclusions, 'extra_development_above_embedded_budget': c['extra_development'],
                'future_tax_shield': (future_exclusions+c['extra_development'])*shield,
                'future_after_tax_charge': future_after_tax_charge,
                'gaap_ni': gaap_ni, 'gaap_eps': gaap_eps,
                'eps_gap_to_adjusted': f['adjusted_eps']-gaap_eps,
                'adjusted_eps_after_extra_development': f['adjusted_eps']-c['extra_development']*(1-shield)/shares,
                'pe_at_reference_price': a['reference_price']/gaap_eps if gaap_eps > 0 else None}
        item['fy28_gaap_eps_growth_vs_fy27_pct'] = (item['years']['FY28']['gaap_eps']/item['years']['FY27']['gaap_eps']-1)*100
        out['scenarios'].append(item)
    return out


def produce(d):
    out = calculate(d)
    out['input_sha256'] = hashlib.sha256(INPUT.read_bytes()).hexdigest()
    out['tax_shield_sensitivity'] = [
        {'marginal_tax_shield': tax,
         'scenarios': [{'id': s['id'], 'FY27_gaap_eps': s['years']['FY27']['gaap_eps'], 'FY28_gaap_eps': s['years']['FY28']['gaap_eps']}
                       for s in calculate(d,tax)['scenarios']]}
        for tax in d['assumptions']['tax_shield_sensitivity']]
    out['share_sensitivity_fixed_ni'] = [
        {'scenario_id': s['id'], 'fy28_net_income_held_fixed': s['years']['FY28']['gaap_ni'],
         'cases': [{'diluted_shares': n, 'gaap_eps': s['years']['FY28']['gaap_ni']/n}
                   for n in d['assumptions']['fy28_shares_sensitivity']]}
        for s in out['scenarios']]
    a = d['assumptions']
    price = a['reference_price']
    out['valuation_hurdles'] = [{'pe': pe, 'required_gaap_eps': price/pe,
                               'required_net_income_at_fy28_shares': price/pe*d['forecast_anchors']['FY28']['diluted_shares_assumed']}
                              for pe in a['valuation_pe_hurdles']]
    out['required_adjusted_eps_by_scenario_at_50x_gaap'] = [
        {'scenario_id': s['id'],
         'required_gaap_eps': price/50,
         'required_baseline_adjusted_eps_before_extra_development': price/50+s['years']['FY28']['eps_gap_to_adjusted'],
         'increase_over_adjusted_consensus_pct': ((price/50+s['years']['FY28']['eps_gap_to_adjusted'])/d['forecast_anchors']['FY28']['adjusted_eps']-1)*100}
        for s in out['scenarios']]
    out['third_party_net_income_crosscheck'] = {
        year: {'forecast_net_income': d['gaap_consensus_crosscheck'][year+'_net_income'],
               'eps_using_our_assumed_shares': d['gaap_consensus_crosscheck'][year+'_net_income']/d['forecast_anchors'][year]['diluted_shares_assumed']}
        for year in ('FY27','FY28')}
    b = a['budget_check']
    budgets = []
    for year in ('FY27','FY28'):
        f = d['forecast_anchors'][year]
        mixes = [b['FY27_hardware_revenue']] if year=='FY27' else b['FY28_hardware_revenue_cases']
        for chip in mixes:
            gp = (f['revenue']-chip)*b['ip_gross_margin_before_restored_costs']+chip*b['hardware_gross_margin_before_restored_costs']
            ni = f['adjusted_eps']*f['diluted_shares_assumed']
            op = ni/(1-b['adjusted_effective_tax_rate'])-b['interest_income']
            budgets.append({'fiscal_year': year,'revenue':f['revenue'],'hardware_revenue':chip,
                            'implied_adjusted_gross_profit':gp,
                            'implied_total_adjusted_opex_including_development':gp-op,
                            'includes_chip_rd':True,'classification':'mix_and_cost_budget_sensitivity_not_segment_guidance'})
    out['implied_opex_budgets'] = budgets
    out['development_cost_sensitivity'] = {
        'extra_100m_reduces_fy28_gaap_eps_by': 100*(1-a['marginal_tax_shield'])/d['forecast_anchors']['FY28']['diluted_shares_assumed'],
        'ordinary_rd_deducted_again': False}
    return out


def check(d, r):
    for period in r['historical_reconciliations'].values():
        assert period['residual'] == 0
    assert d['historical']['Q2_FY27']['sbc_restored'] == 377
    assert d['historical']['H1_FY27']['sbc_restored'] == 720
    assert d['historical']['compensation_backlog']['recognition_schedule_available'] is False
    assert all(s['years']['FY27']['historical_gaap_ni_retained']==400 for s in r['scenarios'])
    by = {s['id']: s for s in r['scenarios']}
    for year in ('FY27','FY28'):
        assert by['flat_q2_costs']['years'][year]['gaap_eps'] > by['higher_compensation']['years'][year]['gaap_eps'] > by['development_overrun']['years'][year]['gaap_eps']
        expected = next(s for s in d['scenario_inputs'] if s['id']=='development_overrun')[year]['extra_development']*(1-d['assumptions']['marginal_tax_shield'])/d['forecast_anchors'][year]['diluted_shares_assumed']
        actual = by['higher_compensation']['years'][year]['gaap_eps']-by['development_overrun']['years'][year]['gaap_eps']
        assert math.isclose(expected,actual,abs_tol=1e-12)
    for row in r['share_sensitivity_fixed_ni']:
        assert row['cases'][0]['gaap_eps'] > row['cases'][-1]['gaap_eps']
    h = d['historical']['H1_FY27']
    assert h['gaap_rd'] > h['adjusted_rd'] > 0
    assert r['development_cost_sensitivity']['ordinary_rd_deducted_again'] is False
    assert all(b['includes_chip_rd'] for b in r['implied_opex_budgets'])
    assert produce(d) == r


def render(d, r):
    lines=['# ARM forward GAAP EPS bridge — November 20, 2026', '',
           'Conditional research model; amounts USD millions unless specified. Fiscal years end March 31. Price reference $152.20, not a live quote.', '',
           '## Historical reconciliation', '',
           'H1 FY27: $1,046 adjusted net income − $720 SBC − $138 employer taxes − $12 acquisition costs − $7 other costs + $108 recorded investment gains + $123 tax reconciliation = **$400 GAAP net income**.', '',
           'Q2 FY27: $566 − $377 − $48 − $12 − $20 investment losses + $21 tax reconciliation = **$130 GAAP net income**. P&L SBC includes $1m software SBC amortization; the cash-flow SBC line alone is $376m.', '',
           '## Forward bridge', '',
           'Adjusted EPS anchors: FY27 $2.27; FY28 $3.09 (S&P Global via Stock Analysis, Nov17 vintage). Assumed diluted shares: 1.09B and 1.11B. Reference marginal tax shield: 15%; future equity gains assumed zero. FY27 H1 actual income, equity gains and taxes remain fixed.', '',
           '| Scenario | FY27 GAAP EPS | FY28 GAAP EPS | FY28 P/E at $152.20 |',
           '|---|---:|---:|---:|']
    for s in r['scenarios']:
        y27,y28=s['years']['FY27'],s['years']['FY28']
        lines.append(f"| {s['label']} | ${y27['gaap_eps']:.2f} | ${y28['gaap_eps']:.2f} | {y28['pe_at_reference_price']:.1f}x |")
    lines += ['', 'These are conditional cases, not probabilities, company guidance or a precisely bounded forecast range.', '',
              '## FY28 cost restoration', '',
              '| USD millions | Flat Q2 costs | Higher compensation | Plus development overrun |',
              '|---|---:|---:|---:|']
    for label,k in [('Adjusted net income anchor','adjusted'),('SBC','sbc'),('Employer taxes, net','employer_tax'),('Acquisition costs','acquisition'),('Extra development above embedded budget','extra_development')]:
        vals=[]
        for s in d['scenario_inputs']:
            vals.append(d['forecast_anchors']['FY28']['adjusted_eps']*d['forecast_anchors']['FY28']['diluted_shares_assumed'] if k=='adjusted' else s['FY28'][k])
        lines.append('| '+label+' | '+' | '.join(f'{v:,.1f}' for v in vals)+' |')
    lines += ['', 'Higher compensation assumes SBC $1.85B in FY27 and $2.40B in FY28. Employer taxes and acquisition costs are separately restored. The development-overrun case deducts another $100M in FY27 H2 and $300M in FY28 beyond expenses already embedded in adjusted EPS.', '',
              'The filing discloses $3.4066B of unrecognized Omnibus-plan compensation, expected over a weighted-average 1.5 years, plus $20.2M ESPP cost. This motivates sensitivity; it DOES NOT establish an annual recognition schedule. New awards, vesting, forfeitures, capitalization and tax effects can change actual expense. A lower current stock price does not automatically remeasure existing equity awards at the new price; grant-date fair value applies.', '',
              '## Development expenses and double-counting', '',
              'H1 R&D was $1.695B GAAP and $1.077B adjusted. Ordinary engineers, design services, cloud compute and other chip-development costs are already expensed inside adjusted operating costs. Restore excluded compensation/acquisition amounts once; do not subtract all GAAP R&D from adjusted earnings again. Depreciation and actual GAAP capitalization remain as reported. Arm does not disclose an independently forecastable silicon-only R&D budget.', '',
              '## Tax sensitivity', '',
              '| Marginal tax shield | FY28 flat-cost EPS | FY28 higher-compensation EPS | FY28 development-overrun EPS |',
              '|---|---:|---:|---:|']
    for tax in r['tax_shield_sensitivity']:
        lines.append(f"| {tax['marginal_tax_shield']:.0%} | "+' | '.join(f"${s['FY28_gaap_eps']:.2f}" for s in tax['scenarios'])+' |')
    lines += ['', 'Marginal tax shield is a modeling assumption, not the effective tax rate or issuer tax guidance. H1 actual taxes are not recalculated. Tax benefits could be lower, higher or deferred.', '',
              '## Operating-budget cross-check', '',
              'At $8.37B FY28 revenue, 98% illustrative IP gross margin and 35% hardware gross margin before restored exclusions, the total adjusted opex budget consistent with $3.09 EPS is:', '',
              '| FY28 hardware revenue | Implied total adjusted opex, including development |',
              '|---|---:|']
    for b in r['implied_opex_budgets']:
        if b['fiscal_year']=='FY28':
            lines.append(f"| ${b['hardware_revenue']/1000:.2f}B | ${b['implied_total_adjusted_opex_including_development']/1000:.2f}B |")
    lines += ['', 'Assumes $120M net interest and 15% adjusted tax rate. Product mix is hypothetical, not an analyst segment breakdown. The total revenue anchor is held fixed: this is a mix sensitivity, not a claim that incremental chip sales destroy earnings. Every $100M additional pre-tax development spending beyond the embedded budget cuts FY28 GAAP EPS by about $0.077 under the reference assumptions.', '',
              '## Independent aggregate cross-check', '',
              'Third-party forecast net income: FY27 $1.190B and FY28 $1.939B. Using our assumed shares implies EPS of about $1.09 and $1.75. These are EPS derived from separate aggregate net-income forecasts; they are not a matched analyst-panel GAAP EPS bridge. They illustrate a less demanding cost outcome than the higher-compensation sensitivity.', '',
              '## Valuation hurdle', '',
              '| P/E on future GAAP earnings | Required EPS at $152.20 | Required net income at 1.11B shares |',
              '|---|---:|---:|']
    for h in r['valuation_hurdles']:
        lines.append(f"| {h['pe']}x | ${h['required_gaap_eps']:.2f} | ${h['required_net_income_at_fy28_shares']/1000:.2f}B |")
    lines += ['', '**Assessment:** the current evidence establishes a reduced premium, not demonstrated cheapness on FY28 GAAP earnings. The royalty/content thesis can still support substantial long-term upside, but the price requires faster earnings conversion, a sustained premium multiple or materially stronger outcomes beyond this horizon. This model is not a DCF, price target or floor.', '',
              '## Review and next action', '',
              'Local validation checks exact historical reconciliation, actual-H1 retention, P&L SBC, no repeated ordinary R&D deduction, monotonic cost sensitivity, fixed-NI share sensitivity and deterministic replay. Exact-head CI and independent financial review are separate gates. Next action: review the expense recognition, tax and product-mix assumptions against the next issuer disclosure.', '',
              '## Sources', '']
    for key,v in d['sources'].items():
        lines.append(f"- {key}: {v['url']}")
    return '\n'.join(lines)+'\n'


def main():
    d=json.loads(INPUT.read_text())
    r=produce(d)
    if '--check' in sys.argv:
        check(d,r)
    (ROOT/'gaap-results.json').write_text(json.dumps(r,indent=2)+'\n')
    (ROOT/'GAAP_BRIDGE.md').write_text(render(d,r))
    buf=io.StringIO(); writer=csv.writer(buf)
    writer.writerow(['scenario','fiscal_year','period_end','adjusted_eps_anchor','gaap_eps_modeled','pe_at_152_20','assumed_diluted_shares_m','restored_costs_m','extra_development_m','tax_shield_rate'])
    for s in r['scenarios']:
        for year,y in s['years'].items():
            writer.writerow([s['id'],year,y['period_end'],y['adjusted_eps_anchor'],y['gaap_eps'],y['pe_at_reference_price'],y['diluted_shares'],y['full_year_restored_expenses'],y['extra_development_above_embedded_budget'],r['marginal_tax_shield']])
    (ROOT/'gaap-bridge.csv').write_text(buf.getvalue())
    print(json.dumps({'checks':'passed' if '--check' in sys.argv else 'not requested',
                      'historical':r['historical_reconciliations'],
                      'scenarios':[{'id':s['id'],'FY27_eps':s['years']['FY27']['gaap_eps'],'FY28_eps':s['years']['FY28']['gaap_eps'],'FY28_pe':s['years']['FY28']['pe_at_reference_price']} for s in r['scenarios']],
                      'budget':r['implied_opex_budgets']},indent=2))

if __name__=='__main__':
    main()
