"""Purpose-specific, offline temporal qualification; no fetch or admission authority."""
from datetime import datetime
import json
from jsonschema import Draft202012Validator
from referencing import Registry
from orchestration import component_conformance as cc
from orchestration.clean_templates import lifecycle as lc
from orchestration.clean_templates.semantic import obj, array


def stamp(value):
    return datetime.fromisoformat(value.upper().replace('Z', '+00:00'))


def digest(value):
    return cc.digest(cc.canonical(value))


def profile():
    text = {'type': 'string', 'minLength': 1, 'pattern': r'\S'}
    date = {'type': 'string', 'format': 'date-time'}
    natural = {'type': 'integer', 'minimum': 0}
    ref = cc.SCHEMA['$defs']['artifact_ref']
    base = lc.read('lifecycle.schema.json')['properties']['request']['properties']
    request = obj({**{k: base[k] for k in ('request_id', 'idempotency_key', 'input_revision', 'source_revision')},
        'purpose': {'enum': ['current', 'historical_as_of']},
        'session': text, 'adjustment_basis': text,
        'current': {'anyOf': [{'type': 'null'}, obj({
            'max_watermark_age_seconds': natural, 'max_observation_age_seconds': natural,
            'refresh': obj({'owner': {'const': '_FETCH'},
                            'max_attempts': {'type': 'integer', 'minimum': 0, 'maximum': 3},
                            'deadline': date})})]},
        'historical': {'anyOf': [{'type': 'null'}, obj({
            'start': date, 'end': date, 'as_of': date, 'pinned_generation': text,
            'revision_policy': {'enum': ['as_of_visible', 'invalidate_on_known_correction']}})]}})
    content = obj({'generation_id': text, 'revision_id': text, 'available_at': date,
        'session': text, 'adjustment_basis': text, 'event_watermark': date,
        'provenance': ref, 'coverage': array(obj({'start': date, 'end': date,
            'status': {'enum': ['observed', 'no_trade', 'unknown']}, 'evidence': ref}), minItems=1)})
    packet = obj({'synthetic': {'const': True}, 'request': request,
        'generation': obj({'content': content, 'artifact': ref}),
        'observation': obj({'retrieved_at': date, 'source_observed_at': date,
                            'last_successful_generation': text}),
        'cache_policy': obj({'stored_at': date, 'max_age_seconds': natural}),
        'entitlement': obj({'granted': {'type': 'boolean'}, 'evidence': ref,
                           'allowed_purposes': array({'enum': ['current', 'historical_as_of']}, uniqueItems=True)}),
        'corrections': array(obj({'supersedes_generation': text, 'replacement_generation': text,
                                  'available_at': date, 'status': {'enum': ['resolved', 'conflicting']},
                                  'evidence': ref})),
        'refresh_attempts_used': natural,
        'acceptance': {'anyOf': [{'type': 'null'}, obj({
            'request_sha256': base['input_revision'], 'generation_sha256': base['input_revision'],
            'revision_view_sha256': base['input_revision']})]}})
    return packet, request


def evaluate(packet, *, expected_request, now):
    """Qualify supplied declarations; expected_request pins intent/cutoff externally.

    Artifact hashes prove internal integrity only. Source availability, coverage,
    entitlement and correction ledger completeness require owner attestation.
    """
    result = {'valid': False, 'errors': [], 'execution_authorized': False,
              'acceptance_current': False, 'cache_refresh_due': False,
              'owner_refresh_request': None}
    if not isinstance(now, str) or not cc.valid_datetime(now):
        result['errors'] = ['INVALID_NOW']
        return result
    packet_schema, request_schema = profile()
    errors = []
    for label, value, schema in [('packet', packet, packet_schema),
                                  ('expected_request', expected_request, request_schema)]:
        errors.extend(label + ': ' + e.message for e in Draft202012Validator(
            schema, format_checker=cc.FORMATS, registry=Registry()).iter_errors(value))
    if errors:
        result['errors'] = sorted(set(errors))
        return result
    request, generation = packet['request'], packet['generation']
    content, observation = generation['content'], packet['observation']
    instant = stamp(now)
    if request != expected_request:
        errors.append('REQUEST_OR_AS_OF_CHANGED')
    if digest(content) != generation['artifact']['sha256'] or request['input_revision'] != digest(content):
        errors.append('GENERATION_INTEGRITY_MISMATCH')
    if not packet['entitlement']['granted'] or request['purpose'] not in packet['entitlement']['allowed_purposes']:
        errors.append('ENTITLEMENT_REQUIRED')
    for key in ('session', 'adjustment_basis'):
        if request[key] != content[key]:
            errors.append(key.upper() + '_MISMATCH')
    for value in (content['available_at'], content['event_watermark'], observation['retrieved_at'],
                  observation['source_observed_at'], packet['cache_policy']['stored_at']):
        if stamp(value) > instant:
            errors.append('FUTURE_OBSERVATION')
    if (stamp(observation['retrieved_at']) < stamp(content['available_at']) or
            stamp(observation['source_observed_at']) < stamp(content['available_at'])):
        errors.append('OBSERVATION_PRECEDES_REVISION')
    result['cache_refresh_due'] = (instant - stamp(packet['cache_policy']['stored_at'])).total_seconds() > packet['cache_policy']['max_age_seconds']
    historical = request['purpose'] == 'historical_as_of'
    policy = request['historical'] if historical else request['current']
    if policy is None or request['current' if historical else 'historical'] is not None:
        errors.append('EXPLICIT_PURPOSE_POLICY_REQUIRED')
        result['errors'] = sorted(set(errors))
        return result
    cutoff = stamp(policy['as_of']) if historical else instant
    if (cutoff > instant or stamp(content['available_at']) > cutoff or
            stamp(content['event_watermark']) > cutoff):
        errors.append('REVISION_AFTER_AS_OF')
    if stamp(content['event_watermark']) > stamp(content['available_at']):
        errors.append('REVISION_PRECEDES_EVENT')
    corrections = []
    for correction in packet['corrections']:
        if stamp(correction['available_at']) > instant:
            errors.append('FUTURE_CORRECTION_DECLARATION')
        if (not historical or policy['revision_policy'] == 'invalidate_on_known_correction' or
                stamp(correction['available_at']) <= cutoff):
            corrections.append(correction)
            if correction['supersedes_generation'] == content['generation_id']:
                errors.append('CONFLICTING_REVISION' if correction['status'] == 'conflicting' else 'PINNED_GENERATION_SUPERSEDED')
    if historical:
        start, end = stamp(policy['start']), stamp(policy['end'])
        if start >= end or end > cutoff:
            errors.append('INVALID_HISTORICAL_INTERVAL')
        if policy['pinned_generation'] != content['generation_id']:
            errors.append('PINNED_GENERATION_MISMATCH')
    else:
        start = end = None
        if observation['last_successful_generation'] != content['generation_id']:
            errors.append('LAST_SUCCESSFUL_GENERATION_MISMATCH')
        if (instant - stamp(content['event_watermark'])).total_seconds() > policy['max_watermark_age_seconds']:
            errors.append('LATEST_WATERMARK_STALE')
        if (instant - stamp(observation['source_observed_at'])).total_seconds() > policy['max_observation_age_seconds']:
            errors.append('SOURCE_OBSERVATION_STALE')
    cursor, previous_end = start, None
    watermark_covered = False
    for segment in sorted(content['coverage'], key=lambda s: stamp(s['start'])):
        left, right = stamp(segment['start']), stamp(segment['end'])
        if left >= right or (previous_end is not None and left < previous_end):
            errors.append('INVALID_OR_OVERLAPPING_COVERAGE')
        previous_end = right
        if historical and right > cutoff:
            errors.append('COVERAGE_AFTER_AS_OF')
        if left <= stamp(content['event_watermark']) < right and segment['status'] != 'unknown':
            watermark_covered = True
        relevant = not historical or (right > start and left < end)
        if relevant and segment['status'] == 'unknown':
            errors.append('UNKNOWN_COVERAGE')
        if historical and relevant:
            if left > cursor:
                errors.append('MISSING_HISTORICAL_RANGE')
            cursor = max(cursor, min(right, end))
    if historical and cursor < end:
        errors.append('MISSING_HISTORICAL_RANGE')
    if not historical and not watermark_covered:
        errors.append('LATEST_WATERMARK_NOT_COVERED')
    view_sha = digest(sorted(corrections, key=cc.canonical))
    acceptance = packet['acceptance']
    if acceptance is not None and acceptance != {'request_sha256': digest(request),
            'generation_sha256': digest(content), 'revision_view_sha256': view_sha}:
        errors.append('STALE_ACCEPTANCE')
    # This is a bounded owner request proposal, never dispatch or refresh permission.
    stale = {'LATEST_WATERMARK_STALE', 'SOURCE_OBSERVATION_STALE'}
    if (not historical and set(errors) and set(errors) <= stale and
            packet['refresh_attempts_used'] < policy['refresh']['max_attempts'] and
            instant < stamp(policy['refresh']['deadline'])):
        result['owner_refresh_request'] = {'owner': '_FETCH', 'request_sha256': digest(request),
                                         'reason': sorted(set(errors)), 'execution_authorized': False}
    result.update(valid=not errors, errors=sorted(set(errors)),
                  acceptance_current=not errors and acceptance is not None)
    return result


if __name__ == '__main__':
    fixture = lc.read('temporal.examples.json')
    print(json.dumps({name: evaluate(value, expected_request=value['request'], now=fixture['evaluation_time'])
                      for name, value in fixture['examples'].items()}, sort_keys=True))
