"""B04 read-only, fixed-date SMH/SOXX forward valuation reconciliation.

All values are conditional look-through calculations, not issuer-published
multiples or standalone ETF earnings per share. No implicit source lookups.
"""
import hashlib
import json
from decimal import Decimal
from lookthrough import calculate, instant, number

VERSION = 'etf-peer-compare@0.1.0'
YEARS = ('2027', '2028')


def compare_funds(request):
    if request.get('schema') != 'basket.etf_peer_comparison_input@1':
        raise ValueError('versioned input contract required')
    as_of = instant(request['as_of'])
    effective_date = request['holdings_effective_date']
    quote_time = request['equity_market_cap_as_of']
    if instant(quote_time) > as_of:
        raise ValueError('future market capitalization')
    if effective_date > request['as_of'][:10]:
        raise ValueError('future holdings effective date')
    funds = request['funds']
    if len(funds) != 2 or {f.get('ticker') for f in funds} != {'SMH', 'SOXX'}:
        raise ValueError('exactly SMH and SOXX required')
    outputs = {}
    kinds = set()
    for fund in funds:
        if fund['as_of'] != request['as_of']:
            raise ValueError('as-of mismatch')
        if fund.get('holdings_effective_date') != effective_date:
            raise ValueError('holdings effective-date mismatch')
        if fund.get('equity_market_cap_as_of') != quote_time:
            raise ValueError('equity market-cap timestamp mismatch')
        if fund.get('currency') != 'USD':
            raise ValueError('USD-normalized issuer snapshot required')
        if fund.get('source_class') != 'issuer_primary':
            raise ValueError('issuer-primary fund holdings required')
        if not fund.get('source_manifest'):
            raise ValueError('source manifest required')
        result = calculate(fund)
        outputs[fund['ticker']] = result
        kinds.add(fund.get('data_kind'))
    if len(kinds) != 1 or kinds.pop() not in {'synthetic_test', 'verified_observation'}:
        raise ValueError('mixed or unclassified data kinds')
    years = {}
    for year in YEARS:
        lhs = outputs['SMH']['years'][year]
        rhs = outputs['SOXX']['years'][year]
        contributions = {}
        for ticker, record in [('SMH', lhs), ('SOXX', rhs)]:
            contributions[ticker] = {c['id']: number(c['contribution']) for c in record['contributions']}
        coverage = {k: outputs[k]['years'][year]['equity_coverage_ratio'] for k in ('SMH', 'SOXX')}
        complete = all(outputs[k]['years'][year]['pe'] is not None for k in ('SMH', 'SOXX'))
        if complete:
            yield_difference = number(lhs['earnings_yield_known_contribution']) - number(rhs['earnings_yield_known_contribution'])
            names = sorted(set(contributions['SMH']) | set(contributions['SOXX']))
            attribution = {n: str(contributions['SMH'].get(n, Decimal(0)) - contributions['SOXX'].get(n, Decimal(0))) for n in names}
            if sum(map(number, attribution.values()), Decimal(0)) != yield_difference:
                raise ValueError('attribution does not reconcile')
            lower_multiple = 'SMH' if number(lhs['pe']) < number(rhs['pe']) else ('SOXX' if number(rhs['pe']) < number(lhs['pe']) else 'tie')
        else:
            yield_difference = None
            attribution = None
            lower_multiple = None
        years[year] = {
            'earnings_yield': {k: outputs[k]['years'][year]['earnings_yield_known_contribution'] for k in ('SMH', 'SOXX')},
            'forward_pe': {k: outputs[k]['years'][year]['pe'] for k in ('SMH', 'SOXX')},
            'equity_estimate_coverage': coverage,
            'yield_spread_smh_minus_soxx': str(yield_difference) if yield_difference is not None else None,
            'yield_spread_contributions': attribution,
            'lower_forward_multiple_indicator': lower_multiple,
            'status': 'mathematically_comparable' if complete else 'unrankable_incomplete_or_nonpositive',
        }
    digest = hashlib.sha256(json.dumps(request, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {
        'schema': 'basket.etf_peer_comparison_output@1', 'engine_version': VERSION,
        'as_of': request['as_of'], 'holdings_effective_date': effective_date,
        'equity_market_cap_as_of': quote_time, 'input_sha256': digest,
        'data_kind': funds[0]['data_kind'], 'funds': ['SMH', 'SOXX'], 'years': years,
        'disclosure': 'A lower forward multiple is not a risk-adjusted preference; no ETF EPS/share, fees, distribution forecasts, or statistically validated upside is implied. Issuer provenance is asserted by upstream adapter, not verified here.',
    }
