"""Offline dispatch proposal; never starts workers or writes economic data."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

CAPABILITIES = {
    'market': 'B02', 'filings_earnings': 'B03',
    'capacity_contracts': 'B03', 'memory_optics_power': 'B03',
    'relationships': 'B05', 'valuation': 'B04',
    'perspectives_signals': 'B21',
}

def instant(value):
    if not isinstance(value, str):
        raise ValueError('Timestamp string required')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Timezone required')
    return dt.astimezone(timezone.utc)

def discover(root):
    entities = {}
    for folder in sorted(Path(root).iterdir()):
        if not folder.is_dir():
            continue
        entity = json.loads((folder / 'entity.json').read_text())
        if entity.get('id') != folder.name or not re.fullmatch(r'[A-Z0-9._-]+', folder.name):
            raise ValueError('Invalid entity identity: ' + folder.name)
        if entity.get('type') not in ('public_equity', 'private_company'):
            raise ValueError('Unsupported entity type: ' + folder.name)
        entities[folder.name] = entity
    if not entities:
        raise ValueError('Empty canonical universe')
    return entities

def compile_plan(entities, coverage, as_of, candidates=()):
    now = instant(as_of)
    if not isinstance(entities, dict) or not entities:
        raise ValueError('Nonempty canonical entity mapping required')
    if not isinstance(coverage, dict):
        raise ValueError('Coverage mapping required')
    if isinstance(candidates, str) or not isinstance(candidates, (list, tuple, set)):
        raise ValueError('Candidate ID collection required')
    if any(not isinstance(t, str) or not re.fullmatch(r'[A-Z0-9._-]+', t) for t in candidates):
        raise ValueError('Invalid candidate identity')
    tasks, matrix = [], []
    for ticker, entity in sorted(entities.items()):
        if not isinstance(entity, dict) or entity.get('id') != ticker or entity.get('type') not in ('public_equity', 'private_company'):
            raise ValueError('Invalid canonical entity: ' + str(ticker))
        ticker_coverage = coverage.get(ticker, {})
        if not isinstance(ticker_coverage, dict):
            raise ValueError('Invalid ticker coverage: ' + ticker)
        for capability, owner in CAPABILITIES.items():
            state = ticker_coverage.get(capability, {})
            if not isinstance(state, dict):
                raise ValueError('Invalid capability coverage: ' + ticker + ':' + capability)
            status = 'missing'
            if capability == 'market' and entity['type'] != 'public_equity':
                status = 'not_applicable'
            elif state.get('status') in ('blocked', 'unsupported', 'conflicted'):
                status = state['status']
            elif state:
                try:
                    observed = instant(state['observed_at'])
                    available = instant(state['first_available_at'])
                    expires = instant(state['expires_at'])
                    if any(not isinstance(state.get(k), list) or not state[k] or
                           any(not isinstance(v, str) or not v.strip() for v in state[k])
                           for k in ('record_ids', 'source_ids')):
                        status = 'unverified'
                    elif max(observed, available) > now or expires <= max(observed, available):
                        status = 'invalid_time'
                    else:
                        status = 'fresh' if now < expires else 'stale'
                except (KeyError, TypeError, ValueError):
                    status = 'unverified'
            row = {'ticker': ticker, 'capability': capability, 'owner': owner, 'status': status}
            matrix.append(row)
            if status not in ('fresh', 'not_applicable'):
                tasks.append(dict(row, task_key=f'capture:{ticker}:{capability}',
                                  action='resolve_gap' if status in ('blocked', 'unsupported', 'conflicted') else 'capture_or_refresh',
                                  dispatch_state='proposal_requires_owner_claim'))
    unknown = sorted(set(candidates) - set(entities))
    return {'schema': 'basket.capture_dispatch.proposal@1', 'as_of': as_of,
            'canonical_count': len(entities), 'coverage': matrix, 'tasks': tasks,
            'unregistered_candidates': unknown, 'live_verified': False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tickers', required=True)
    parser.add_argument('--coverage', type=Path)
    parser.add_argument('--candidates', type=Path, help='JSON array; does not admit candidates')
    parser.add_argument('--as-of', required=True)
    args = parser.parse_args()
    result = compile_plan(discover(args.tickers),
                          json.loads(args.coverage.read_text()) if args.coverage else {},
                          args.as_of,
                          json.loads(args.candidates.read_text()) if args.candidates else [])
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
