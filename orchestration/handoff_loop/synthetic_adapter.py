"""Pure synthetic input port. Never authenticates evidence or authorizes effects."""
from copy import deepcopy
import json
import math
import re

from .core import criterion_digest, digest, evaluate, require, subject_digest, validate

SCHEMA = 'basket.handoff_synthetic_input@0.1-draft'
FLAGS = {'online', 'single_writer', 'active', 'approval_pending', 'handoff_requested', 'checkpoint_due'}
IDENTITY = {'environment_id', 'host', 'owner', 'session', 'branch', 'worktree', 'scope'}
FIELDS = FLAGS | IDENTITY


def shape(value, keys):
    require(type(value) is dict and set(value) == set(keys.split()), 'unsupported or missing fields')


def nonblank(value):
    require(type(value) is str and bool(value.strip()), 'nonblank string required')


def json_value(value):
    if type(value) is dict:
        require(all(type(k) is str for k in value), 'JSON keys must be strings')
        for item in value.values():
            json_value(item)
    elif type(value) is list:
        for item in value:
            json_value(item)
    else:
        require(type(value) in (str, int, float, bool, type(None)), 'non-JSON value')
        if type(value) is float:
            require(math.isfinite(value), 'nonfinite number')


def load_json(text):
    """Strict optional wire decoder; duplicate JSON keys must not be overwritten."""
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def sources_by_id(rows):
    require(type(rows) is list and bool(rows), 'sources required')
    result = {}
    for row in rows:
        shape(row, 'id identity revision')
        for value in row.values():
            nonblank(value)
        require(row['identity'].startswith('synthetic://'), 'synthetic source namespace required')
        require(len(row['identity']) > len('synthetic://') and re.fullmatch('[0-9a-f]{40}', row['revision']) is not None, 'exact source identity/revision required')
        require(row['id'] not in result, 'duplicate source ID')
        result[row['id']] = row
    return result


def normalize(state, envelope, pins, *, now, max_age=300):
    """Pins are separately supplied expectations, not authority manufactured here.

    Invalid input raises ValueError without mutation or partial receipts. Unknown
    or unavailable values return incomplete, not False or an evaluator-ready packet.
    """
    for value in (state, envelope, pins):
        json_value(value)
    require(type(now) in (int, float) and math.isfinite(now), 'finite evaluation time required')
    require(type(max_age) in (int, float) and math.isfinite(max_age) and max_age > 0, 'positive finite freshness bound required')
    shape(pins, 'subject_digest revision sources')
    shape(envelope, 'schema mode wake_id subject_digest revision sources observations receipts')
    require(envelope['schema'] == SCHEMA and envelope['mode'] == 'synthetic', 'synthetic schema/mode required')
    require(type(pins['revision']) is str and re.fullmatch('[0-9a-f]{40}', pins['revision']) is not None, 'exact Git revision required')
    require(pins['subject_digest'] == subject_digest(state), 'pinned subject mismatch')
    require(envelope['subject_digest'] == pins['subject_digest'] and envelope['revision'] == pins['revision'], 'envelope subject/revision mismatch')
    expected_sources = sources_by_id(pins['sources'])
    sources = sources_by_id(envelope['sources'])
    require(sources == expected_sources, 'source identity/revision mismatch')
    nonblank(envelope['wake_id'])
    require(type(envelope['observations']) is list and type(envelope['receipts']) is list, 'record arrays required')
    seen = set()

    def record(row, extra):
        shape(row, 'id source_id subject_digest revision observed_at ' + extra)
        nonblank(row['id'])
        require(row['id'] not in seen, 'duplicate evidence ID')
        seen.add(row['id'])
        nonblank(row['source_id'])
        require(row['source_id'] in sources, 'unsupported source')
        require(row['subject_digest'] == pins['subject_digest'] and row['revision'] == pins['revision'], 'record subject/revision mismatch')
        stamp = row['observed_at']
        require(type(stamp) in (int, float) and math.isfinite(stamp) and 0 <= now - stamp <= max_age, 'stale/unknown/future observation time')
        return sources[row['source_id']]

    observed, availability, provenance = {}, {}, {}
    for row in envelope['observations']:
        source = record(row, 'field availability value')
        field = row['field']
        require(type(field) is str and field in FIELDS and field not in availability, 'unsupported/duplicate observation field')
        require(row['availability'] in ('available', 'unknown', 'unavailable'), 'unsupported availability')
        availability[field] = row['availability']
        provenance[field] = dict(source_id=row['source_id'], source=source['identity'], source_revision=source['revision'],
                                 subject_digest=row['subject_digest'], revision=row['revision'], observed_at=row['observed_at'])
        if row['availability'] != 'available':
            require(row['value'] is None, 'unknown/unavailable value must be null')
            continue
        if field in FLAGS:
            require(type(row['value']) is bool, 'actual boolean required')
        else:
            require(row['value'] == state['claim'][field], 'observed identity mismatch')
        observed[field] = deepcopy(row['value'])
    require(set(availability) == FIELDS, 'required observation missing')

    nodes = {row['id']: row for row in state['objectives']}
    receipts = {}
    for row in envelope['receipts']:
        source = record(row, 'kind payload')
        payload = row['payload']
        require(row['kind'] in ('test', 'acceptance'), 'unsupported receipt kind')
        if row['kind'] == 'test':
            shape(payload, 'objective command executed result tests failures errors skipped')
            require(payload['executed'] is True and payload['result'] == 'pass', 'test must have executed and passed')
            nonblank(payload['command'])
            require(type(payload['tests']) is int and payload['tests'] > 0, 'positive test count required')
            require(all(type(payload[k]) is int and payload[k] == 0 for k in ('failures', 'errors', 'skipped')), 'test failures/errors/skips')
        else:
            shape(payload, 'objective criterion criterion_digest result reviewer artifact')
            require(payload['result'] == 'pass', 'acceptance must pass')
            nonblank(payload['reviewer'])
            nonblank(payload['artifact'])
        nonblank(payload['objective'])
        require(payload['objective'] in nodes, 'unknown receipt objective')
        node = nodes[payload['objective']]
        require(row['revision'] in node['artifact_revisions'] and row['id'] in node['evidence'], 'unbound receipt revision/reference')
        if row['kind'] == 'acceptance':
            gates = {gate['id']: gate for gate in node['acceptance']}
            nonblank(payload['criterion'])
            require(payload['criterion'] in gates, 'unknown criterion')
            gate = gates[payload['criterion']]
            require(payload['criterion_digest'] == criterion_digest(gate) and row['id'] in gate['evidence'], 'unbound criterion evidence')
        receipts[row['id']] = dict(deepcopy(payload), kind=row['kind'], source=source['identity'],
                                   source_id=row['source_id'], source_revision=source['revision'], revision=row['revision'],
                                   subject_digest=row['subject_digest'], observed_at=row['observed_at'], synthetic=True)
    validate(state, receipts)
    complete = all(value == 'available' for value in availability.values())
    observation = None
    if complete:
        stamps = [p['observed_at'] for p in provenance.values()] + [r['observed_at'] for r in receipts.values()]
        observation = dict(observed, wake_id=envelope['wake_id'], verified_at=min(stamps))
    return dict(schema='basket.handoff_synthetic_normalized@0.1-draft', mode='synthetic',
                status='ready' if complete else 'incomplete', observation=observation,
                receipts=dict(sorted(receipts.items())) if complete else {},
                availability=dict(sorted(availability.items())), provenance=dict(sorted(provenance.items())),
                input_digest=digest(envelope), pins_digest=digest(pins),
                evaluated_at=now, max_age=max_age,
                evidence_truth_verified=False, execution_authorized=False)


def evaluate_synthetic(state, envelope, pins, *, now, max_age=300):
    """Offline simulation only. Never dispatches, persists or grants authority."""
    packet = normalize(state, envelope, pins, now=now, max_age=max_age)
    decision = (evaluate(state, packet['observation'], packet['receipts'], now=now, max_age=max_age)
                if packet['status'] == 'ready' else
                dict(action='blocked', reason='unknown/unavailable synthetic observations', dispatch='not_attempted',
                     execution='not_attempted', publication='unknown', acceptance='not_established', delivery='not_established'))
    return dict(packet, simulated_decision=decision)
