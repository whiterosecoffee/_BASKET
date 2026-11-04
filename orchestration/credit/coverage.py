"""Dated audit projection, never a security master or market-data writer."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

SCOPE_SHA = '321c93c281aeeb7d63b5d107cca6a320070d5f02'
SCOPE_BLOB = '876c729bedeaebfeb867a51cde591118cf32aa75'
RESOURCES = ('bond_transactions', 'bond_quotes', 'cds', 'loan_terms',
             'sofr_curve', 'treasury_curve', 'issuer_filings', 'maturities',
             'covenants', 'collateral', 'guarantees', 'fund_flows')
NON_BORROWERS = {'index', 'futures_contract', 'fx_pair'}
TYPES = NON_BORROWERS | {'fund_or_etp', 'equity_or_depositary_receipt'}


def project(manifest):
    records = manifest['records']
    symbols = [r['symbol'] for r in records]
    if len(symbols) != len(set(symbols)) or len(records) != manifest['count']:
        raise ValueError('scope count or duplicate symbol mismatch')
    if any(r['instrument_type'] not in TYPES for r in records):
        raise ValueError('unreviewed instrument type')
    if manifest.get('schema') != 'basket.scope_manifest@draft1':
        raise ValueError('unreviewed scope contract')
    rows = []
    for record in sorted(records, key=lambda r: r['symbol']):
        symbol, kind = record['symbol'], record['instrument_type']
        # Source classifications are provisional. A fund is not assumed debt-free.
        applicability = ('not_applicable_direct_issuer_conditional_on_scope_type'
                         if kind in NON_BORROWERS else
                         'fund_lookthrough_and_legal_borrower_review_required'
                         if kind == 'fund_or_etp' else 'unavailable_issuer_mapping_and_debt_review')
        resources = {}
        for resource in RESOURCES:
            state = 'unavailable_not_audited_at_issuer_level'
            if kind in NON_BORROWERS and resource not in ('sofr_curve', 'treasury_curve', 'fund_flows'):
                state = 'not_applicable_direct_issuer_conditional_on_scope_type'
            if resource in ('sofr_curve', 'treasury_curve'):
                state = 'unavailable_matched_curve_snapshot_and_rights_unverified'
            if resource == 'fund_flows':
                state = 'unavailable_source_and_exposure_mapping_unverified'
            resources[resource] = state
        if symbol == 'CRWV':
            for resource in ('loan_terms', 'issuer_filings', 'maturities', 'covenants', 'collateral', 'guarantees'):
                resources[resource] = 'historical_draft_evidence_requires_primary_reverification'
        rows.append({'scope_symbol_ref': symbol, 'scope_type_provisional': kind,
                     'issuer_id': None, 'debt_applicability': applicability,
                     'evidence_refs': ['https://github.com/whiterosecoffee/_BASKET/blob/6d82bccacaaba9855ef6bd27c64d72eb0514c8c9/research/CRWV/debt/2026-10-22/debt-stack.json'] if symbol == 'CRWV' else [],
                     'resources': resources, 'current_verified_pricing': False,
                     'observed_premium_bps': None, 'justified_premium_bps': None,
                     'mispricing_residual_bps': None, 'model_accuracy': None})
    canonical = json.dumps(manifest, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return {'artifact': 'credit-stage0-audit-projection', 'as_of': '2026-11-04',
            'intake_issue': 136, 'worker_issue': 162,
            'source': {'path': '_TICKERS/manifest.json', 'commit': SCOPE_SHA,
                       'git_blob': SCOPE_BLOB, 'semantic_sha256': hashlib.sha256(canonical.encode()).hexdigest(),
                       'status': 'unmerged_provisional_scope_not_security_master'},
            'coverage_basis': 'repository_evidence_only_not_exhaustive_external_source_scan',
            'resource_defaults': {'observed_at': None, 'available_at': None, 'expires_at': None,
                                  'entitlement': 'unverified',
                                  'reason': 'No canonical current matched credit observations verified by this audit'},
            'counts': {'scope_identifiers': len(rows),
                       'types': dict(sorted(Counter(r['instrument_type'] for r in records).items())),
                       'verified_current_pricing': 0, 'verified_issuer_identity': 0},
            'rows': rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    path = Path(args.manifest)
    raw = path.read_bytes()
    actual_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if actual_blob != SCOPE_BLOB:
        raise ValueError('source bytes do not match pinned Git blob')
    result = project(json.loads(raw))
    Path(args.output).write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
