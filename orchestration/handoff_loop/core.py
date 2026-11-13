"""Small offline policy kernel. The trusted observation adapter is a separate port."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile

SCHEMA = 'basket.handoff_objectives@0.2-draft'
DIMENSION_SUCCESSES = {
    'scheduling': {'scheduled'}, 'dispatch': {'dispatched'},
    'execution': {'executed', 'operational'}, 'publication': {'published'},
    'acceptance': {'accepted'}, 'delivery': {'delivered'},
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def criterion_digest(gate):
    return digest({'id': gate['id'], 'condition': gate['condition']})


def subject_digest(state):
    """Bind dimension evidence to exact ownership and objective contents."""
    return digest({'claim': state['claim'], 'objectives': state['objectives']})


def validate_dimensions(state, receipts):
    dimensions = state['dimensions']
    require(isinstance(dimensions, dict) and set(dimensions) == set(DIMENSION_SUCCESSES), 'dimension fields')
    revisions = {v for row in state['objectives'] for v in row['artifact_revisions']}
    for name, value in dimensions.items():
        require(isinstance(value, dict) and set(value) == {'status', 'evidence'}, 'dimension shape')
        status, refs = value['status'], value['evidence']
        require(isinstance(status, str) and status in DIMENSION_SUCCESSES[name] | {'unknown', 'not_established', 'pending', 'blocked'}, 'dimension status')
        require(isinstance(refs, list) and all(isinstance(r, str) for r in refs) and len(set(refs)) == len(refs), 'dimension evidence references')
        if status in DIMENSION_SUCCESSES[name]:
            require(bool(refs), 'dimension receipt required')
            for ref in refs:
                require(ref in receipts, 'unverified dimension evidence')
                r = receipts[ref]
                require(r.get('kind') == 'dimension' and r.get('dimension') == name and r.get('status') == status and bool(r.get('source')) and r.get('revision') in revisions and r.get('subject_digest') == subject_digest(state), 'dimension receipt mismatch')
            if name == 'acceptance':
                require(all(row['status'] == 'accepted' for row in state['objectives']), 'overall acceptance requires all objectives')
        else:
            require(not refs, 'non-success dimension cannot carry success evidence')


def validate(state, receipts):
    """Receipts must come from the caller's independent verifier, never the snapshot."""
    require(state['schema'] == SCHEMA, 'unknown schema')
    require(type(state['revision']) is int and state['revision'] >= 0, 'revision')
    require(len(set(state['processed_wakes'])) == len(state['processed_wakes']), 'duplicate wake history')
    require(state['canonical_record'].startswith('https://github.com/'), 'canonical record')
    coverage = state['source_coverage']
    require(set(coverage) == {'verified_read_watermark', 'persisted_ranges', 'unknown_ranges'}, 'coverage fields')
    require(isinstance(coverage['persisted_ranges'], list) and isinstance(coverage['unknown_ranges'], list), 'coverage ranges')
    rows = state['objectives']
    nodes = {x['id']: x for x in rows}
    require(len(nodes) == len(rows) and bool(rows), 'unique objective IDs')
    for key, row in nodes.items():
        require(bool(key) and bool(row['owner']) and bool(row['scope']) and bool(row['next_action']), 'objective identity/scope')
        require(row['status'] in {'pending', 'active', 'blocked', 'accepted'}, 'objective status')
        require(isinstance(row['blockers'], list), 'blockers')
        edges = row['depends_on'] + ([row['parent']] if row['parent'] else [])
        require(len(set(row['depends_on'])) == len(row['depends_on']), 'duplicate dependency')
        require(all(x in nodes and x != key for x in edges), 'unknown/self reference')
        evidence = row['evidence']
        require(len(set(evidence)) == len(evidence), 'duplicate evidence')
        for ref in evidence:
            require(ref in receipts, 'unverified evidence')
            receipt = receipts[ref]
            require(receipt['kind'] != 'session-start' and receipt['source'] and receipt['revision'], 'invalid evidence')
            require(receipt['revision'] in row['artifact_revisions'], 'stale artifact evidence')
        require(bool(row['acceptance']), 'missing acceptance conditions')
        for gate in row['acceptance']:
            require(gate['id'] and gate['condition'], 'acceptance identity')
            require(set(gate['evidence']).issubset(evidence), 'unknown gate evidence')
            require(all(receipts[r]['kind'] == 'acceptance' and receipts[r].get('objective') == key and receipts[r].get('criterion') == gate['id'] and receipts[r].get('criterion_digest') == criterion_digest(gate) for r in gate['evidence']), 'acceptance criterion receipt mismatch')
        require(len({a['id'] for a in row['acceptance']}) == len(row['acceptance']), 'duplicate acceptance ID')
        if row['status'] == 'accepted':
            require(not row['blockers'], 'accepted with blockers')
            require(all(a['evidence'] for a in row['acceptance']), 'acceptance evidence missing')
            require(all(receipts[r]['kind'] == 'acceptance' and receipts[r].get('objective') == key and receipts[r].get('criterion') == a['id'] for a in row['acceptance'] for r in a['evidence']), 'acceptance not independently verified')
            children = [x['id'] for x in rows if x['parent'] == key]
            require(all(nodes[x]['status'] == 'accepted' for x in children + row['depends_on']), 'parent/dependency acceptance gate')
    # Parent-child ordering and dependency ordering must also be jointly acyclic.
    graph = {key: list(row['depends_on']) + [x['id'] for x in rows if x['parent'] == key] for key, row in nodes.items()}
    visiting, done = set(), set()
    def visit(key):
        require(key not in visiting, 'cyclic hierarchy/dependencies')
        if key in done:
            return
        visiting.add(key)
        for dep in graph[key]:
            visit(dep)
        visiting.remove(key)
        done.add(key)
    for key in nodes:
        visit(key)
    validate_dimensions(state, receipts)


def evaluate(state, observation, receipts, *, now, max_age=300):
    """Pure decision. Supplied observations must be verified outside this module."""
    validate(state, receipts)
    o = observation
    def result(action, reason):
        return {'action': action, 'reason': reason, 'dispatch': 'not_attempted',
                'execution': 'not_attempted', 'publication': 'unknown',
                'acceptance': 'not_established', 'delivery': 'not_established'}
    if not o.get('online', False):
        return result('blocked', 'workstation offline; park')
    claim = state['claim']
    if not (0 <= now - o.get('verified_at', -1e20) <= max_age):
        return result('blocked', 'stale or unknown observation')
    if any(not claim.get(k) or o.get(k) != claim[k] for k in ('environment_id', 'host', 'owner', 'session', 'branch', 'worktree', 'scope')) or o.get('single_writer') is not True:
        return result('blocked', 'host/ownership not verified')
    if not o.get('wake_id') or any(type(o.get(k)) is not bool for k in ('active', 'approval_pending', 'handoff_requested', 'checkpoint_due')):
        return result('blocked', 'activity observation incomplete')
    if o['wake_id'] in state['processed_wakes']:
        return result('no-change', 'duplicate wake')
    if o.get('active'):
        return result('coalesce', 'same owner is active')
    if o.get('approval_pending'):
        return result('blocked', 'approval pending; not inactivity')
    if o.get('blocker_fingerprint'):
        return result('no-change' if o['blocker_fingerprint'] == state.get('blocker_fingerprint') else 'blocked', 'blocked condition; no retry')
    if o.get('handoff_requested'):
        transfer = o.get('transfer', {})
        ack = transfer.get('replacement_ack', {})
        required = {'branch': claim['branch'], 'scope': claim['scope'], 'data_access': True, 'outstanding_task': state['next_action']}
        if transfer.get('old_writer_retired') is True and ack.get('owner') and ack['owner'] != claim['owner'] and all(ack.get(k) == v for k, v in required.items()):
            return result('handoff-ready', 'retirement and replacement acknowledgement supplied; transfer not executed')
        return result('request checkpoint', 'transfer retirement/acknowledgement incomplete')
    if o.get('checkpoint_due'):
        return result('request checkpoint', 'bounded checkpoint needed')
    nodes = {x['id']: x for x in state['objectives']}
    outstanding = [x for x in nodes.values() if x['status'] != 'accepted']
    if any(x['status'] in {'pending', 'active'} and not x['blockers'] and all(nodes[d]['status'] == 'accepted' for d in x['depends_on']) for x in outstanding):
        return result('continue', 'same authorized owner/session/branch only')
    if outstanding:
        return result('blocked', 'objectives have unresolved blockers/dependencies')
    return result('no-change', 'no outstanding objective')


def persist(path, expected_digest, update, receipts, observation, *, now):
    """Exclusive lock + content CAS + atomic replace + readback. Never breaks locks.

    Update runs after the latest state is read. Crash leftovers block until an
    operator verifies writer retirement. This is local-filesystem persistence.
    """
    path = Path(path)
    lock = path.with_suffix(path.suffix + '.lock')
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    temporary = None
    try:
        os.close(fd)
        current = json.loads(path.read_text(encoding='utf-8'))
        require(digest(current) == expected_digest, 'checkpoint CAS conflict')
        decision = evaluate(current, observation, receipts, now=now)
        require(decision['reason'] not in {'host/ownership not verified', 'stale or unknown observation', 'workstation offline; park', 'activity observation incomplete'}, 'write admission rejected')
        if decision['reason'] == 'duplicate wake':
            return current
        updated = update(deepcopy(current))
        require(updated['revision'] == current['revision'] + 1, 'revision must increment')
        require(updated['claim'] == current['claim'], 'transfer requires separate ownership protocol')
        require(updated['canonical_record'] == current['canonical_record'], 'canonical record immutable')
        expected_wakes = current['processed_wakes'] + [observation['wake_id']]
        require(updated['processed_wakes'] in (current['processed_wakes'], expected_wakes), 'callback cannot rewrite wake history')
        # Wake consumption is part of this atomic commit, never a callback obligation.
        updated['processed_wakes'] = expected_wakes
        old_nodes = {x['id']: x for x in current['objectives']}
        new_nodes = {x['id']: x for x in updated['objectives']}
        require(set(old_nodes).issubset(new_nodes), 'objective IDs cannot disappear')
        require(all(old_nodes[k][field] == new_nodes[k][field] for k in old_nodes for field in ('parent', 'owner', 'scope')), 'objective identity cannot change')
        for key, row in old_nodes.items():
            old_gates = {g['id']: g for g in row['acceptance']}
            new_gate_ids = {g['id'] for g in new_nodes[key]['acceptance']}
            require(set(old_gates).issubset(new_gate_ids), 'acceptance criterion IDs cannot disappear')
            for gate in new_nodes[key]['acceptance']:
                require(gate['id'] not in old_gates or criterion_digest(gate) == criterion_digest(old_gates[gate['id']]), 'changed condition requires a new criterion ID')
        require({digest(x) for x in current['source_coverage']['persisted_ranges']}.issubset({digest(x) for x in updated['source_coverage']['persisted_ranges']}), 'persisted coverage cannot regress')
        validate(updated, receipts)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as f:
            temporary = f.name
            json.dump(updated, f, indent=2, allow_nan=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
        temporary = None
        require(json.loads(path.read_text(encoding='utf-8')) == updated, 'readback mismatch')
        return updated
    finally:
        if temporary:
            os.unlink(temporary)
        os.unlink(lock)
