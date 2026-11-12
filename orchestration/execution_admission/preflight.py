"""Pure, offline evidence evaluation. No collection, launch, locks or writes."""
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).parent
REQUEST_SCHEMA = json.loads((ROOT / 'request.schema.json').read_text(encoding='utf-8'))
RECEIPT_SCHEMA = json.loads((ROOT / 'receipt.schema.json').read_text(encoding='utf-8'))


def fingerprint(value):
    """Hash JSON values; callers must supply JSON, never arbitrary Python objects."""
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _time(value):
    if not isinstance(value, str) or not re.fullmatch(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', value):
        raise ValueError('RFC3339 timestamp with timezone required')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timezone required')
    return result


# jsonschema's optional RFC3339 dependency is not assumed installed.
FORMATS = FormatChecker()


@FORMATS.checks('date-time', raises=(ValueError, TypeError))
def _valid_time(value):
    _time(value)
    return True


def _path(value):
    # This bounded profile supports concrete repository paths only. Globs,
    # absolute paths, traversal and platform-dependent aliases fail closed.
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_./-]+', value):
        raise ValueError('unsupported path')
    parts = value.split('/')
    if any(p in ('', '.', '..') or p.endswith('.') for p in parts):
        raise ValueError('noncanonical path')
    return '/'.join(parts).casefold()


def _within(path, root):
    return path == root or path.startswith(root + '/')


def _overlap(a, b):
    return _within(a, b) or _within(b, a)


def evaluate(request, observation, trusted, *, now):
    """Evaluate supplied declarations against separately supplied trusted pins.

    `trusted` must come from the controller, `observation` from its collector.
    Their authenticity is outside this pure function. An eligible receipt is
    never execution permission; the executor must recheck and acquire its lock.
    Invalid JSON types/nonfinite numbers or invalid `now` raise ValueError.
    Structurally invalid JSON contracts return a rejected receipt.
    """
    hashes = [fingerprint(x) for x in (request, observation, trusted)]
    current = _time(now)
    reasons = []
    def reject(code):
        if code not in reasons:
            reasons.append(code)
    for label, value, schema in (
        ('request', request, REQUEST_SCHEMA),
        ('observation', observation, REQUEST_SCHEMA['$defs']['observation']),
        ('trusted', trusted, REQUEST_SCHEMA['$defs']['trusted']),
    ):
        if not Draft202012Validator(schema, format_checker=FORMATS).is_valid(value):
            reject('schema:' + label)
    if not reasons:
        r, o, t = request, observation, trusted
        if hashes[0] != t['request_sha256']:
            reject('request_not_controller_approved')
        if r['policy_version'] != t['policy_version']:
            reject('policy_mismatch')
        if r['identity'] != t['identity'] or o['identity'] != t['identity']:
            reject('identity_mismatch')
        if not re.fullmatch(r'work/[1-9][0-9]*-[a-z0-9][a-z0-9-]*', t['identity']['branch']):
            reject('unscoped_branch')
        if not t['task_registered']:
            reject('task_unregistered')
        if o['collector'] != t['collector']:
            reject('collector_mismatch')
        if any(x['host'].casefold() != t['host'].casefold() or x['os'] != t['os']
               for x in (r['executor'], o)):
            reject('executor_mismatch')
        age = (current - _time(o['observed_at'])).total_seconds()
        if age < 0 or age > t['max_evidence_age_seconds']:
            reject('evidence_stale_or_future')
        if not o['isolated_worktree']:
            reject('worktree_not_isolated')
        if not o['purpose_present'] or o['manifest_sha256'] != r['manifest']['sha256']:
            reject('purpose_or_manifest_missing')
        if (r['authority']['source'] != t['authority_source'] or
                r['authority']['inherited_from'] != t['authority_parent']):
            reject('authority_mismatch')
        try:
            roots = [_path(p) for p in r['owned_folders']]
            writes = [_path(p) for p in r['allowed_writes']]
            inherited = [_path(p) for p in r['authority']['scope']]
            permitted = [_path(p) for p in t['allowed_scope']]
            _path(r['manifest']['path'])
            if not any(_within(_path(r['manifest']['path']), p) for p in roots):
                reject('manifest_outside_owned_folder')
            if (any(not any(_within(p, a) for a in permitted) for p in inherited) or
                any(not any(_within(p, a) for a in inherited) for p in roots) or
                any(not any(_within(p, a) for a in roots) for p in writes)):
                reject('scope_escalation')
            for claim in o['ownership']:
                paths = [_path(p) for p in claim['paths']]
                if any(_overlap(a, b) for a in roots for b in paths):
                    if any(claim[k] != t['identity'][k] for k in ('task_id','owner','branch','worktree')):
                        reject('ownership_overlap')
        except ValueError:
            reject('unsupported_path')
        if not o['ownership_complete'] or not o['writers_complete']:
            reject('incomplete_writer_inventory')
        active = [w for w in o['writers'] if w['active']]
        mode = r['lifecycle']['mode']
        # Even an identical task/owner tuple may hide a second process.
        if (mode != 'continuation' and active) or len(active) > 1 or any(w[k] != t['identity'][k]
                                 for w in active for k in ('task_id','owner','branch','worktree')):
            reject('competing_writer')
        def indexed(items):
            result = {x['id']: x for x in items}
            if len(result) != len(items):
                reject('duplicate_evidence_id')
            return result
        resources = indexed(o['resources'])
        prereqs = indexed(o['prerequisites'])
        for ids, values, code in ((r['executor']['resources'], resources, 'resource_unconfirmed'),
                                  (r['prerequisites'], prereqs, 'prerequisite_unconfirmed')):
            if any(i not in values or not values[i]['confirmed'] for i in ids):
                reject(code)
        inputs = indexed(o['inputs'])
        if len({x['id'] for x in r['inputs']}) != len(r['inputs']):
            reject('duplicate_input_id')
        for item in r['inputs']:
            proof = inputs.get(item['id'])
            if proof is None or not proof['readable']:
                reject('input_unreadable')
                continue
            if not proof['schema_valid'] or proof['schema'] != item['schema']:
                reject('input_schema_mismatch')
            if proof['sha256'] != item['sha256']:
                reject('input_integrity_mismatch')
            age = (current - _time(proof['observed_at'])).total_seconds()
            if age < 0 or age > item['max_age_seconds']:
                reject('input_stale_or_future')
        if not set(r['permitted_effects']).issubset(t['effects']):
            reject('effect_not_permitted')
        if o['prior_effects'] == 'uncertain':
            reject('prior_effects_uncertain')
        if o['prior_effects'] == 'confirmed_complete':
            reject('already_completed_reconcile_only')
        if o['prior_idempotency_key'] not in (None, r['recovery']['idempotency_key']):
            reject('idempotency_key_mismatch')
        if mode != 'continuation' and t['continuation_binding'] is not None:
            reject('unexpected_continuation_binding')
        if mode == 'new':
            if not t['new_identity_confirmed']:
                reject('new_identity_unconfirmed')
            if o['continuation'] is not None or o['transfer'] is not None:
                reject('unexpected_lifecycle_evidence')
        elif mode == 'continuation':
            continuation = o['continuation']
            binding = t['continuation_binding']
            if continuation is None or continuation['identity'] != t['identity']:
                reject('continuation_ownership_changed')
            if (binding is None or continuation is None or
                any(continuation[k] != binding[k] for k in ('session_id','lease_id')) or
                not continuation['lease_confirmed'] or
                _time(continuation['lease_expires_at']) <= current):
                reject('continuation_lease_unconfirmed')
            if len(active) != 1:
                reject('continuation_writer_missing_or_multiple')
            elif binding is None or any(active[0][k] != binding[k] for k in ('session_id','lease_id')):
                reject('continuation_writer_binding_mismatch')
            if o['transfer'] is not None:
                reject('unexpected_lifecycle_evidence')
        else:
            if o['continuation'] is not None:
                reject('unexpected_lifecycle_evidence')
            transfer = o['transfer']
            if (transfer is None or not transfer['stopped'] or not transfer['confirmed'] or
                not r['lifecycle']['previous_owner'] or not r['lifecycle']['transfer_ref'] or
                transfer['previous_owner'] != r['lifecycle']['previous_owner'] or
                transfer['ref'] != r['lifecycle']['transfer_ref'] or
                transfer['previous_owner'] == t['identity']['owner']):
                reject('transfer_not_confirmed_stopped')
        if mode != 'transfer' and (r['lifecycle']['previous_owner'] is not None or
                                   r['lifecycle']['transfer_ref'] is not None):
            reject('unexpected_transfer_declaration')
    offline = isinstance(observation, dict) and observation.get('online') is False
    decision = 'parked' if offline else ('rejected' if reasons else 'eligible')
    if offline:
        reject('offline_parking_only')
    receipt = {
        'schema': 'basket.execution_admission_receipt@1',
        'policy_version': request.get('policy_version') if isinstance(request, dict) and isinstance(request.get('policy_version'), str) else None,
        'request_sha256': hashes[0], 'observation_sha256': hashes[1], 'trusted_sha256': hashes[2],
        'evaluated_at': now, 'decision': decision, 'reasons': reasons,
        'execution_authorized': False, 'evidence_truth_verified': False,
        'permitted_next': 'park_only' if offline else ('repair_evidence' if reasons else 'executor_recheck'),
    }
    Draft202012Validator(RECEIPT_SCHEMA, format_checker=FORMATS).validate(receipt)
    return receipt
