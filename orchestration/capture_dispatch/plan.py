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
    parser.add_argument('--bindings', type=Path, help='Owner-approved task-key mapping; emit manager queue proposal')
    args = parser.parse_args()
    result = compile_plan(discover(args.tickers),
                          json.loads(args.coverage.read_text()) if args.coverage else {},
                          args.as_of,
                          json.loads(args.candidates.read_text()) if args.candidates else [])
    if args.bindings:
        result = manager_proposal(result, json.loads(args.bindings.read_text()))
    print(json.dumps(result, indent=2))

def manager_proposal(proposal, bindings):
    """Produce queue-shaped input for the existing manager, never mutate its queue.

    Bindings explicitly assign stable queue IDs, scope and dependencies. This
    compiler does not allocate IDs, grant ownership, or start conversations.
    """
    if not isinstance(bindings, dict) or not bindings:
        raise ValueError('Explicit owner-approved bindings required')
    gaps = {task['task_key']: task for task in proposal['tasks']}
    if set(bindings) - set(gaps):
        raise ValueError('Binding does not refer to a current coverage gap')
    tasks, seen = [], set()
    for key, binding in sorted(bindings.items()):
        if not isinstance(binding, dict):
            raise ValueError('Invalid binding')
        tid = binding.get('id')
        if not isinstance(tid, str) or not re.fullmatch(r'T-[0-9]{3,}', tid) or tid in seen:
            raise ValueError('Explicit unique stable task IDs required')
        seen.add(tid)
        gap = gaps[key]
        if binding.get('spark_id') != gap['owner']:
            raise ValueError('Binding changes capability owner')
        scopes = binding.get('write_scope')
        if not isinstance(scopes, list) or not scopes or any(
                not isinstance(p, str) or not p or p.startswith('/') or
                '..' in p or '\\' in p for p in scopes):
            raise ValueError('Explicit safe write scope required')
        allowed = {'B02': ('runtime/', 'fx/', 'tickers/'),
                   'B03': ('research/filings/', 'research/events/', 'tickers/'),
                   'B04': ('engines/valuation/',),
                   'B05': ('research/graph/', 'engines/relationships/', 'tickers/'),
                   'B21': ('engines/narrative/', 'research/narrative/',)}[gap['owner']]
        for scope in scopes:
            if scope.startswith('tickers/'):
                suffixes = {'B02': ('/history.jsonl', '/history.meta.json', '/intraday/**', '/live/**'),
                            'B03': ('/events.json',), 'B05': ('/relationships.json',)}
                if not scope.endswith(suffixes.get(gap['owner'], ())):
                    raise ValueError('Canonical ticker scope belongs to another owner')
            elif not scope.startswith(allowed):
                raise ValueError('Scope outside capability owner domain')
        if binding.get('priority') not in ('P0', 'P1', 'P2'):
            raise ValueError('Explicit priority required')
        acceptance = binding.get('acceptance')
        if not isinstance(acceptance, list) or not acceptance or any(not isinstance(a, str) or not a.strip() for a in acceptance):
            raise ValueError('Evidence-backed acceptance criteria required')
        dependencies = binding.get('depends_on', [])
        if not isinstance(dependencies, list):
            raise ValueError('Dependency list required')
        for dep in dependencies:
            if not isinstance(dep, dict) or not re.fullmatch(r'T-[0-9]{3,}', str(dep.get('task_id'))) or dep.get('gate') not in ('merged', 'issue_exists', 'ci_passed_on_head'):
                raise ValueError('Invalid dependency')
        issue, pr = binding.get('issue_number'), binding.get('pr_number')
        if any(x is not None and (type(x) is not int or x <= 0) for x in (issue, pr)) or (pr and not issue):
            raise ValueError('Invalid issue/PR identity')
        tasks.append({'id': tid, 'spark_id': gap['owner'],
                      'title': f"{gap['ticker']}: {gap['capability']}",
                      'objective': f"{gap['action']} for {key}; preserve source/revision/freshness evidence",
                      'priority': binding['priority'],
                      'mode': 'resume_existing_worker' if issue else 'launch_new_worker',
                      'acceptance': acceptance, 'depends_on': dependencies,
                      'write_scope': scopes, 'issue_number': issue, 'pr_number': pr})
    for task in tasks:
        if any(d['task_id'] not in seen for d in task['depends_on']):
            raise ValueError('Dependency outside proposed batch; compose with existing queue through its owner')
    return {'schema': 'basket.capture_manager_bridge.proposal@1',
            'as_of': proposal['as_of'], 'live_verified': False,
            'queue_proposal': {'active_worker_limit': 3, 'tasks': tasks},
            'unbound_gap_keys': sorted(set(gaps) - set(bindings)),
            'unregistered_candidates': proposal['unregistered_candidates'],
            'requires_existing_manager_validation': True}

if __name__ == '__main__':
    main()
