"""Thin QC intake adapter; canonical project tasks stay in GitHub Issues.

Reuses worker-task schema and ownership helpers. No network, scheduler, code
execution, new worker creation or claim of atomic multiwriter ownership.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import PurePosixPath
import re

from orchestration.worker_protocol import validate_schema, permitted, declared_subset, read, ROOT

QUEUE = 'https://github.com/whiterosecoffee/_BASKET/issues/136'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def request_id(request):
    value = copy.deepcopy({k: v for k, v in request.items() if k != 'request_id'})
    value['artifacts'] = sorted(value['artifacts'], key=lambda a: (a['path'], a['revision'], a['role']))
    value['item_ids'] = sorted(value['item_ids'])
    return digest(value)


def validate_request(request):
    require(set(request) == {'request_id', 'task', 'source_pr', 'artifacts', 'item_ids',
                             'review_kind'}, 'unexpected or missing intake field')
    errors = validate_schema(request['task'], 'task')
    require(not errors, 'invalid worker task: ' + '; '.join(errors))
    task = request['task']
    catalog = read(ROOT / 'orchestration/sparks.json')
    owners = {s['id']: s['write_paths'] for s in catalog['sparks']}
    require(task['spark_id'] in owners and all(declared_subset(p, owners[task['spark_id']])
            for p in task['write_paths']), 'task claims another spark domain')
    require(task['task_id'] == f"{task['spark_id']}-{task['issue']['number']}", 'task identity mismatch')
    require(task['issue']['url'] == f"https://github.com/whiterosecoffee/_BASKET/issues/{task['issue']['number']}",
            'issue URL identity mismatch')
    require(task['branch']['name'].startswith(f"work/{task['issue']['number']}-"), 'branch identity mismatch')
    require(type(request['source_pr']) is int and request['source_pr'] > 0, 'invalid PR')
    require(request['review_kind'] == 'closeout_semantic', 'unsupported review kind')
    ids = request['item_ids']
    require(isinstance(ids, list) and ids and all(isinstance(x, str) and x.strip() for x in ids), 'missing inventory')
    require(len(ids) == len(set(ids)), 'duplicate inventory item')
    artifacts = request['artifacts']
    require(isinstance(artifacts, list) and artifacts, 'missing artifacts')
    seen, roles = set(), []
    for artifact in artifacts:
        require(set(artifact) == {'path', 'revision', 'sha256', 'role'}, 'invalid artifact fields')
        path = artifact['path']
        require(isinstance(path, str) and path and not path.startswith('/') and
                '\\' not in path and all(x not in ('', '.', '..') for x in path.split('/')) and
                str(PurePosixPath(path)) == path, 'unsafe artifact path')
        require(permitted(path, task['write_paths']), 'artifact outside source task ownership')
        require(re.fullmatch(r'[0-9a-f]{40}', artifact['revision']) is not None, 'unpinned artifact')
        require(re.fullmatch(r'[0-9a-f]{64}', artifact['sha256']) is not None, 'invalid artifact hash')
        require(artifact['role'] in ('primary', 'handoff'), 'invalid artifact role')
        key = (path, artifact['revision'])
        require(key not in seen, 'duplicate artifact')
        seen.add(key); roles.append(artifact['role'])
    require('primary' in roles and roles.count('handoff') == 1, 'primary and one handoff required')
    require(request['request_id'] == request_id(request), 'request digest mismatch')
    return request


def validate_index(index):
    require(set(index) == {'schema', 'canonical_queue', 'requests'}, 'invalid index fields')
    require(index['schema'] == 'basket.closeout_qc_index@1' and index['canonical_queue'] == QUEUE,
            'wrong canonical queue')
    require(isinstance(index['requests'], list), 'requests must be a list')
    seen = set()
    for request in index['requests']:
        validate_request(request)
        require(request['request_id'] not in seen, 'duplicate request')
        seen.add(request['request_id'])
    return index


def enqueue(index, request):
    """Return unchanged content on replay; caller persists with expected-head CAS."""
    validate_index(index); validate_request(request)
    if any(x['request_id'] == request['request_id'] for x in index['requests']):
        return copy.deepcopy(index)
    result = copy.deepcopy(index)
    result['requests'].append(copy.deepcopy(request))
    return result


def verify_artifacts(request, read_bytes):
    """read_bytes(path, revision) must fetch exact GitHub bytes; errors propagate."""
    validate_request(request)
    for artifact in request['artifacts']:
        data = read_bytes(artifact['path'], artifact['revision'])
        require(isinstance(data, bytes), 'artifact reader must return bytes')
        require(hashlib.sha256(data).hexdigest() == artifact['sha256'], 'artifact hash mismatch')
    return True


def reconcile_inventory(request, read_bytes, source_items):
    """Compare independent source annotations, pinned handoff, and submitted IDs.

    source_items maps IDs to source URLs, derived by the reviewer from available
    conversation/review evidence, NEVER copied blindly from request.item_ids.
    This gate checks explicit ID conservation, not natural-language meaning or
    source authenticity. The reviewer must report unavailable source coverage.
    """
    require(callable(read_bytes), 'inventory review requires pinned artifact reader')
    require(isinstance(source_items, dict) and source_items, 'missing independent source inventory')
    for item, urls in source_items.items():
        require(isinstance(item, str) and item.strip(), 'invalid source item')
        require(isinstance(urls, list) and urls and all(isinstance(url, str) and
                url.startswith('https://github.com/whiterosecoffee/_BASKET/') for url in urls),
                'source item needs repository evidence')
    cache = {}
    def cached(path, revision):
        key = (path, revision)
        if key not in cache:
            cache[key] = read_bytes(path, revision)
        return cache[key]
    verify_artifacts(request, cached)
    handoff = next(a for a in request['artifacts'] if a['role'] == 'handoff')
    text = cached(handoff['path'], handoff['revision']).decode('utf-8')
    # Explicit top-level O1/K1/R1-style records, not incidental prose mentions.
    observed = re.findall(r'^([A-Z][A-Z0-9_-]*[0-9])(?=[: \t])', text, re.M)
    handoff_ids, submitted, sourced = set(observed), set(request['item_ids']), set(source_items)
    duplicates = sorted({item for item in observed if observed.count(item) > 1})
    missing_items = sorted((sourced | handoff_ids) - submitted)
    missing_handoff = sorted((sourced | submitted) - handoff_ids)
    unanchored = sorted((submitted | handoff_ids) - sourced)
    complete = bool(observed) and not (duplicates or missing_items or missing_handoff or unanchored)
    return {'request_id': request['request_id'], 'outcome': 'review' if complete else 'rework',
            'handoff_sha256': handoff['sha256'], 'handoff_item_ids': sorted(handoff_ids),
            'source_items': copy.deepcopy(source_items), 'missing_item_ids': missing_items,
            'missing_handoff_ids': missing_handoff, 'unanchored_item_ids': unanchored,
            'duplicate_handoff_ids': duplicates}


def validate_receipt(receipt, request):
    validate_request(request)
    require(set(receipt) == {'request_id', 'reviewer', 'outcome', 'item_dispositions',
                             'evidence_urls', 'limitations', 'next_action'}, 'invalid receipt fields')
    require(receipt['request_id'] == request['request_id'], 'receipt belongs to another revision')
    require(isinstance(receipt['reviewer'], str) and receipt['reviewer'].strip(), 'missing reviewer')
    require(receipt['outcome'] in ('accepted', 'rework', 'blocked', 'superseded'), 'invalid review outcome')
    require(set(receipt['item_dispositions']) == set(request['item_ids']), 'unaccounted inventory items')
    for value in receipt['item_dispositions'].values():
        require(set(value) == {'state', 'reason', 'destination'}, 'invalid item disposition')
        require(value['state'] in ('completed', 'transfer', 'blocked', 'deferred', 'discarded'), 'invalid item state')
        require(all(isinstance(value[k], str) and value[k].strip() for k in ('reason', 'destination')),
                'missing disposition rationale/destination')
    urls = receipt['evidence_urls']
    require(isinstance(urls, list) and urls and all(isinstance(x, str) and x.startswith('https://github.com/whiterosecoffee/_BASKET/') for x in urls),
            'missing repository evidence')
    require(isinstance(receipt['limitations'], list) and all(isinstance(x, str) for x in receipt['limitations']), 'invalid limitations')
    require(isinstance(receipt['next_action'], str) and receipt['next_action'].strip(), 'missing next action')
    # Presence validation alone NEVER authorizes archive. pending additionally
    # checks verified handoff bytes against independent source annotations.
    return receipt


def pending(index, receipts, priority_issues, *, read_bytes=None, source_items=None):
    """Use B00's supplied issue order, never arrival order or invented priorities.

    Returns unrouted requests separately. Caller must refresh evidence and honor
    dependencies/claims before dispatch; this function never grants authority.
    """
    validate_index(index)
    require(isinstance(priority_issues, list) and all(type(i) is int and i > 0 for i in priority_issues)
            and len(set(priority_issues)) == len(priority_issues), 'invalid priority order')
    requests = {r['request_id']: r for r in index['requests']}
    archived, receipt_ids, inventory_reviews = set(), set(), {}
    for receipt in receipts:
        rid = receipt['request_id']
        require(rid in requests, 'unknown receipt request')
        require(rid not in receipt_ids, 'multiple final receipts require explicit reconciliation')
        receipt_ids.add(rid)
        validate_receipt(receipt, requests[rid])
        if receipt['outcome'] in ('accepted', 'superseded'):
            require(callable(read_bytes) and isinstance(source_items, dict) and rid in source_items,
                    'archive requires pinned bytes and independent source inventory')
            review = reconcile_inventory(requests[rid], read_bytes, source_items[rid])
            inventory_reviews[rid] = review
            if review['outcome'] == 'review':
                archived.add(rid)
    rank = {issue: n for n, issue in enumerate(priority_issues)}
    active = [r for r in index['requests'] if r['request_id'] not in archived]
    ready = [r for r in active if r['task']['issue']['number'] in rank]
    ready.sort(key=lambda r: (rank[r['task']['issue']['number']], r['request_id']))
    return {'ordered_intake': ready,
            'needs_priority': [r for r in active if r['task']['issue']['number'] not in rank],
            'archived_request_ids': sorted(archived), 'inventory_reviews': inventory_reviews}
