"""Receiver and sanitizer evidence checks; synthetic declarations, never live effects."""
import copy
import json
from jsonschema import Draft202012Validator
from referencing import Registry
from orchestration import component_conformance as cc
from orchestration.clean_templates import lifecycle as lc, temporal as tp
from orchestration.clean_templates.semantic import obj, array

MANDATORY = {'integrity', 'provenance', 'privacy'}
DOMAIN = {'low': {'semantic_validity'},
          'high': {'semantic_validity', 'coverage', 'units', 'conflict_resolution', 'independent_review'}}
ORIGINS = ['user_assertion', 'producer_observation', 'independently_verified_evidence']


def profile():
    text = {'type': 'string', 'minLength': 1, 'pattern': r'\S'}
    ref = cc.SCHEMA['$defs']['artifact_ref']
    sha = lc.read('lifecycle.schema.json')['properties']['request']['properties']['input_revision']
    versions = {'schema_version': text, 'sanitizer_revision':
                lc.read('lifecycle.schema.json')['properties']['request']['properties']['source_revision'],
                'configuration_sha256': sha}
    policy = obj({'intended_consumer': text, 'intended_use': text,
                  'risk': {'enum': ['low', 'high']}, 'failure_consequence': text,
                  'requires_private': {'type': 'boolean'},
                  'required_domain_checks': array(text, uniqueItems=True),
                  'allowed_unknowns': array(text, uniqueItems=True),
                  'processing_contract': obj({**versions, 'standardizer_runner_version': text,
                                              'auditor_runner_version': text})})
    binding = {'request_sha256': sha, 'artifact_sha256': sha, 'policy_sha256': sha, 'pipeline_sha256': sha}
    lineage = {**versions, 'actor': text, 'runner_version': text,
               'request_sha256': sha, 'policy_sha256': sha,
               'raw_input_sha256': sha, 'normalized_output_sha256': sha,
               'scope': obj({'purpose': {'enum': ['current', 'historical_as_of']},
                             'coverage_sha256': sha, 'stage': {'const': 'normalized_output'}})}
    transform = obj({**lineage, 'role': {'const': 'standardizer'}})
    audit = obj({**lineage, 'role': {'const': 'independent_auditor'},
                 'results': array(obj({'id': text, 'result': {'enum': ['pass', 'fail', 'unknown']}}))})
    preservation = obj({'original_artifact': ref, 'normalized_artifact': ref,
                        'before_sha256': sha, 'after_sha256': sha,
                        'original_destination': text, 'normalized_destination': text,
                        'mode': {'const': 'separate_output_or_sidecar'}})
    pipeline = obj({'raw_input': obj({'content': {'type': 'string'}, 'artifact': ref}),
                    'normalized_output': ref,
                    'transform': obj({'record': transform, 'artifact': ref}),
                    'audit': obj({'record': audit, 'artifact': ref}),
                    'preservation': obj({'record': preservation, 'artifact': ref})})
    claim = obj({'id': text, 'text': text, 'origin': {'enum': ORIGINS},
                 'status': {'enum': ['asserted', 'observed', 'verified']}, 'evidence': ref})
    packet = obj({'synthetic': {'const': True}, 'temporal': {'type': 'object'}, 'policy': policy,
        'dispatch': {'enum': ['not_sent', 'sent']}, 'producer_result': {'enum': ['unknown', 'pass', 'fail']},
        'placement': obj({'destination_visibility': {'enum': ['private', 'public']},
                          'requires_private': {'type': 'boolean'}, 'artifact_present': {'type': 'boolean'}}),
        'claims': array(claim), 'pipeline': pipeline,
        'checks': array(obj({'id': text, 'result': {'enum': ['pass', 'fail', 'unknown']},
                            'origin': {'enum': ORIGINS}, 'evidence': ref, **binding})),
        'receiver': {'anyOf': [{'type': 'null'}, obj({
            **binding, 'consumer': text, 'purpose': {'enum': ['current', 'historical_as_of']},
            'evidence': ref, 'readback_result': {'enum': ['pass', 'fail', 'unknown']},
            'readback_content': {'type': 'object'},
            'acceptance': {'enum': ['pending', 'accepted', 'rejected']}})]}})
    return packet, policy, array(claim)


def evaluate(packet, *, expected_request, expected_policy, retained_claims, now):
    """Check exact receiver and QC declarations against independently retained inputs.

    No supplied provenance label, hash, signature-shaped ref or file placement is
    authenticated here. Real receiver IO and independent review belong to owners.
    """
    result = {'valid': False, 'errors': [], 'unknowns': [], 'execution_authorized': False,
              'evidence_authenticated': False, 'receiver_acknowledged': False,
              'consumer_acceptance': 'pending', 'consumer_usable': False,
              'quarantine': True, 'state': 'blocked', 'claims': [],
              'use_status': 'blocked', 'failures': []}
    packet_schema, policy_schema, claims_schema = profile()
    errors = []
    for label, value, schema in [('packet', packet, packet_schema),
            ('expected_policy', expected_policy, policy_schema), ('retained_claims', retained_claims, claims_schema)]:
        errors.extend(label + ': ' + e.message for e in Draft202012Validator(
            schema, format_checker=cc.FORMATS, registry=Registry()).iter_errors(value))
    if errors:
        result['errors'] = sorted(set(errors))
        return result
    result['claims'] = copy.deepcopy(packet['claims'])
    supplied_results = packet['checks'] + packet['pipeline']['audit']['record']['results']
    result['unknowns'] = sorted({c['id'] for c in supplied_results if c['result'] == 'unknown'})
    result['failures'] = sorted({c['id'] for c in supplied_results if c['result'] == 'fail'})
    errors.extend('FAILED_CHECK:' + name for name in result['failures'])
    qualification = tp.evaluate(packet['temporal'], expected_request=expected_request, now=now)
    errors.extend('temporal: ' + e for e in qualification['errors'])
    policy = packet['policy']
    if policy != expected_policy:
        errors.append('RISK_POLICY_CHANGED')
    if packet['claims'] != retained_claims:
        errors.append('CLAIM_PROVENANCE_CHANGED')
    statuses = dict(zip(ORIGINS, ['asserted', 'observed', 'verified']))
    ids = set()
    for claim in packet['claims']:
        if claim['id'] in ids:
            errors.append('DUPLICATE_CLAIM')
        ids.add(claim['id'])
        if claim['status'] != statuses[claim['origin']]:
            errors.append('ASSERTION_PROMOTED_TO_VERIFICATION')
    if not DOMAIN[policy['risk']] <= set(policy['required_domain_checks']):
        errors.append('RISK_CHECKS_OMITTED')
    placement = packet['placement']
    if placement['requires_private'] != policy['requires_private']:
        errors.append('PRIVACY_POLICY_MISMATCH')
    if policy['requires_private'] and placement['destination_visibility'] != 'private':
        errors.append('PRIVATE_DESTINATION_REQUIRED')
    if not qualification['valid']:
        result['errors'] = sorted(set(errors))
        return result
    request = packet['temporal']['request']
    artifact = packet['temporal']['generation']['artifact']
    pipeline = packet['pipeline']
    raw = pipeline['raw_input']
    if cc.digest(raw['content'].encode('utf-8')) != raw['artifact']['sha256']:
        errors.append('RAW_INPUT_INTEGRITY_MISMATCH')
    if pipeline['normalized_output'] != artifact or raw['artifact']['ref'] == artifact['ref']:
        errors.append('RAW_NORMALIZED_ARTIFACT_BINDING_MISMATCH')
    contract = policy['processing_contract']
    expected_lineage = {k: contract[k] for k in ('schema_version', 'sanitizer_revision', 'configuration_sha256')}
    expected_lineage.update(request_sha256=tp.digest(request), policy_sha256=tp.digest(policy),
        raw_input_sha256=raw['artifact']['sha256'], normalized_output_sha256=artifact['sha256'],
        scope={'purpose': request['purpose'], 'coverage_sha256': tp.digest(packet['temporal']['generation']['content']['coverage']),
               'stage': 'normalized_output'})
    for stage, version in (('transform', 'standardizer_runner_version'), ('audit', 'auditor_runner_version')):
        record = pipeline[stage]['record']
        if any(record[k] != v for k, v in expected_lineage.items()) or record['runner_version'] != contract[version]:
            errors.append('TRANSFORM_AUDIT_LINEAGE_OR_VERSION_MISMATCH')
    for stage in ('transform', 'audit', 'preservation'):
        if tp.digest(pipeline[stage]['record']) != pipeline[stage]['artifact']['sha256']:
            errors.append('PIPELINE_RECORD_HASH_MISMATCH')
    if pipeline['transform']['record']['actor'] == pipeline['audit']['record']['actor']:
        errors.append('STANDARDIZER_CANNOT_BE_INDEPENDENT_AUDITOR')
    audit_ref = pipeline['audit']['artifact']
    for peer in (raw['artifact'], artifact, pipeline['transform']['artifact'], pipeline['preservation']['artifact']):
        if audit_ref['ref'] == peer['ref'] or audit_ref['sha256'] == peer['sha256']:
            errors.append('AUDIT_EVIDENCE_MUST_BE_DISTINCT')
    preservation = pipeline['preservation']['record']
    if (preservation['original_artifact'] != raw['artifact'] or preservation['normalized_artifact'] != artifact or
            preservation['before_sha256'] != raw['artifact']['sha256'] or
            preservation['after_sha256'] != raw['artifact']['sha256'] or
            preservation['original_destination'] == preservation['normalized_destination']):
        errors.append('ORIGINALS_PRESERVATION_MISMATCH')
    observed_results = sorted((c['id'], c['result']) for c in packet['checks'])
    if sorted((c['id'], c['result']) for c in pipeline['audit']['record']['results']) != observed_results:
        errors.append('AUDIT_RESULTS_MISMATCH')
    binding = {'request_sha256': tp.digest(request), 'artifact_sha256': artifact['sha256'],
               'policy_sha256': tp.digest(policy), 'pipeline_sha256': tp.digest(pipeline)}
    checks = {}
    for check in packet['checks']:
        if check['id'] in checks:
            errors.append('DUPLICATE_SANITIZER_CHECK')
        checks[check['id']] = check
        if any(check[k] != v for k, v in binding.items()):
            errors.append('STALE_SANITIZER_EVIDENCE')
        if check['origin'] == 'user_assertion' and check['result'] == 'pass':
            errors.append('ASSERTION_CANNOT_PASS_SANITIZER_CHECK')
    required = MANDATORY | set(policy['required_domain_checks']) | DOMAIN[policy['risk']]
    for name in sorted(required):
        check = checks.get(name)
        if check is None:
            errors.append('MISSING_CHECK:' + name)
            result['unknowns'].append(name)
        elif check['result'] != 'pass':
            errors.append('CHECK_NOT_PASSED:' + name)
            if check['result'] == 'unknown':
                result['unknowns'].append(name)
        elif name == 'independent_review':
            if check['evidence'] != audit_ref:
                errors.append('AUDIT_RECORD_REQUIRED')
            if check['origin'] != 'independently_verified_evidence':
                errors.append('INDEPENDENT_REVIEW_REQUIRED')
            peers = [artifact] + [c['evidence'] for c in checks.values() if c['id'] != name]
            if any(check['evidence']['ref'] == p['ref'] or check['evidence']['sha256'] == p['sha256'] for p in peers):
                errors.append('INDEPENDENT_EVIDENCE_MUST_BE_DISTINCT')
    for name in result['unknowns']:
        if name not in policy['allowed_unknowns'] or name in required:
            errors.append('UNRESOLVED_UNKNOWN:' + name)
    result['unknowns'] = sorted(set(result['unknowns']))
    quality_errors = list(errors)
    receiver = packet['receiver']
    receipt_errors = []
    if receiver is None:
        errors.append('MISSING_RECEIVER_ACKNOWLEDGMENT')
    else:
        if any(receiver[k] != v for k, v in binding.items()):
            receipt_errors.append('STALE_RECEIVER_BINDING')
        if receiver['consumer'] != policy['intended_consumer'] or receiver['purpose'] != request['purpose']:
            receipt_errors.append('RECEIVER_OR_PURPOSE_MISMATCH')
        if receiver['readback_result'] != 'pass' or tp.digest(receiver['readback_content']) != artifact['sha256']:
            receipt_errors.append('READBACK_NOT_VERIFIED')
            if receiver['readback_result'] == 'unknown':
                result['unknowns'].append('receiver_readback')
        if receiver['evidence']['ref'] == artifact['ref'] or receiver['evidence']['sha256'] == artifact['sha256']:
            receipt_errors.append('RECEIVER_EVIDENCE_MUST_BE_DISTINCT')
        errors.extend(receipt_errors)
        result['receiver_acknowledged'] = not receipt_errors
        if not receipt_errors:
            if not quality_errors and not result['unknowns']:
                result['consumer_acceptance'] = receiver['acceptance']
            if receiver['acceptance'] != 'accepted':
                errors.append('CONSUMER_ACCEPTANCE_PENDING_OR_REJECTED')
    result.update(valid=not errors, errors=sorted(set(errors)), quarantine=bool(quality_errors or receipt_errors),
                  consumer_usable=not errors and not result['unknowns'],
                  use_status='blocked' if errors else ('conditional' if result['unknowns'] else 'qualified'),
                  state='review' if not errors else 'blocked')
    return result


if __name__ == '__main__':
    fixture = lc.read('receiver.examples.json')
    print(json.dumps({name: evaluate(value, expected_request=value['temporal']['request'],
        expected_policy=value['policy'], retained_claims=value['claims'], now=fixture['evaluation_time'])
        for name, value in fixture['examples'].items()}, sort_keys=True))
