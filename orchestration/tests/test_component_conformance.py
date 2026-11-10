"""Reusable boundary checks plus an actual B00 pure-function worked example.

The dated B05 fixture is historical protocol evidence, not current GitHub state.
Schemas created here are local fixture contracts, not registered domain APIs.
"""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from jsonschema import ValidationError
from orchestration import component_conformance as cc
from orchestration import worker_protocol as wp

ROOT = Path(__file__).resolve().parents[2]
STAMP = '2026-11-10T12:00:00Z'


def example(*, stale_ci=False):
    artifacts = {}

    def reference(name, data):
        artifacts[name] = data
        return {'ref': name, 'sha256': cc.digest(data)}

    def binding(name, value, schema):
        schema_ref = reference('fixture://' + name + '.schema', cc.canonical(schema))
        payload = reference('fixture://' + name + '.json', cc.canonical(value))
        source = dict(source_id=name, artifact=payload, record_type='other',
                      subject_id='historical-protocol-fixture', observed_at=None,
                      available_at=None, ingested_at=None, effective_at=None,
                      published_at=None, period=None, session='not_applicable',
                      unit='protocol_record', currency=None, freshness='not_applicable',
                      entitlement='not_required', supersedes=None)
        return dict(schema_ref=schema_ref['ref'], schema_sha256=schema_ref['sha256'],
                    artifact=payload, sources=[source])

    examples = ROOT / 'orchestration/examples'
    values = dict(task=wp.read(examples / 'B05.task.json'),
                  report=wp.read(examples / 'B05.resolution.json'),
                  github=wp.read(examples / 'github-evidence-2026-10-16.json'),
                  spark_catalog=wp.read(ROOT / 'orchestration/sparks.json'))
    if stale_ci:
        for run in values['github']['workflow_runs']:
            run['head_sha'] = '0' * 40
    schemas = {name: wp.read(ROOT / ('schemas/worker-' + kind + '.v1.json'))
               for name, kind in [('task', 'task'), ('report', 'resolution'), ('github', 'evidence')]}
    schemas['spark_catalog'] = {'type': 'object', 'required': ['sparks'],
                               'properties': {'sparks': {'type': 'array', 'minItems': 1}}}
    inputs = {name: binding(name, value, schemas[name]) for name, value in values.items()}
    output = wp.evidence_check(**values)  # Reuse existing implementation, never copy it.
    output_schema = dict(type='object', additionalProperties=False,
                        required=list(output), properties={
        'task_id': {'type': 'string'}, 'spark_id': {'type': 'string'},
        'observed_at': {'type': ['string', 'null']},
        'worker_reported_disposition': {'type': 'string'},
        'b00_evidence_phase': {'type': 'string'},
        'checks_passed_on_pr_head': {'type': 'integer', 'minimum': 0},
        'mandatory_acceptance_unresolved': {'type': 'array'},
        'worker_blockers': {'type': 'array'}, 'errors': {'type': 'array'},
        'warnings': {'type': 'array'}, 'recommendation': {'type': 'string'},
        'merge_authorized': {'const': False}})
    outputs = {'verdict': binding('verdict', output, output_schema)}

    def ports(bindings):
        return [dict(name=name, schema_ref=item['schema_ref'], required=True,
                     schema_sha256=item['schema_sha256'], freshness_policy='immutable',
                     source_class='scenario') for name, item in bindings.items()]

    manifest = dict(schema='basket.component_contract@1', component_id='worker.evidence_check',
                    owner_spark='B00', version='1.0.0', determinism='pure',
                    boundary_profile='qualified_refs_v1',
                    assumptions=['Explicit immutable historical fixtures, not live GitHub'],
                    guarantees=['No merge authorization; no external writes'], effects=[],
                    inputs=ports(inputs), outputs=ports(outputs),
                    errors=[dict(code='missing_evidence', retryable=False)],
                    acceptance=dict(test_command='python -m unittest discover -s orchestration/tests -p test_component_conformance.py -v',
                                    minimum_tests=1, fixtures=['B05 historical protocol'], ci_owner='B01'))
    method = reference('fixture://worker_protocol.py',
                       (ROOT / 'orchestration/worker_protocol.py').read_bytes())
    call = dict(contract='basket.component_call@1', component_id=manifest['component_id'],
                contract_version=manifest['version'], run_id='historical-example', as_of=STAMP,
                inputs=inputs, method=method, options=dict(offline=True, seed=None))
    fingerprint = cc.digest(cc.canonical(inputs))  # Explicit fixture-only input hash policy.
    result = dict(contract='basket.component_result@1', component_id=manifest['component_id'],
                  contract_version=manifest['version'], run_id=call['run_id'], as_of=STAMP,
                  status='ok', outputs=outputs,
                  provenance=dict(input_sha256=fingerprint, method=method,
                                  code_sha='a' * 40, generated_at=STAMP),
                  quality=dict(freshness='not_applicable', missing_inputs=[], conflicts=[], warnings=[]),
                  error=None)
    return manifest, call, result, artifacts, fingerprint, output, values


class ComponentConformanceTests(unittest.TestCase):
    def setUp(self):
        (self.manifest, self.call, self.result, self.artifacts,
         self.fingerprint, self.output, self.values) = example()

    def check(self):
        cc.check_exchange(self.manifest, self.call, self.result, self.artifacts,
                          expected_input_sha256=self.fingerprint)

    def rejects(self):
        with self.assertRaises((cc.ConformanceError, ValidationError, ValueError)):
            self.check()

    def test_existing_evaluator_exchange_and_consumer(self):
        self.check()
        ref = self.result['outputs']['verdict']['artifact']['ref']
        consumed = json.loads(self.artifacts[ref])  # Independent consumer reads the port.
        self.assertEqual(consumed['b00_evidence_phase'], 'component_verified_review_pending')
        self.assertFalse(consumed['merge_authorized'])
        self.assertEqual(consumed['errors'], [])
        self.assertEqual(consumed['checks_passed_on_pr_head'], 1)

    def test_existing_evaluator_rejects_stale_ci_evidence(self):
        manifest, call, result, artifacts, fingerprint, output, _ = example(stale_ci=True)
        cc.check_exchange(manifest, call, result, artifacts,
                          expected_input_sha256=fingerprint)
        # The calculation succeeded, but its domain verdict must reject the evidence.
        self.assertEqual(output['b00_evidence_phase'], 'evidence_invalid')
        self.assertTrue(output['errors'])
        self.assertFalse(output['merge_authorized'])

    def test_existing_evaluator_replay_does_not_mutate_inputs(self):
        before = cc.canonical(self.values)
        self.assertEqual(cc.canonical(self.output), cc.canonical(wp.evidence_check(**self.values)))
        self.assertEqual(before, cc.canonical(self.values))

    def test_reference_hashes_are_checked_against_bytes(self):
        for ref in list(self.artifacts):
            with self.subTest(ref=ref):
                saved = self.artifacts[ref]; self.artifacts[ref] = saved + b' '
                self.rejects(); self.artifacts[ref] = saved

    def test_unknown_references_never_open_files_or_network(self):
        self.call['method']['ref'] = 'https://example.invalid/never-fetch'
        with patch('urllib.request.urlopen', side_effect=AssertionError('network')), \
                patch('builtins.open', side_effect=AssertionError('filesystem')):
            self.rejects()

    def test_no_manifest_test_command_execution(self):
        self.manifest['acceptance']['test_command'] = 'DO NOT EXECUTE'
        with patch('subprocess.run', side_effect=AssertionError('execution')):
            self.check()

    def test_component_version_and_request_identity(self):
        for obj, key in [(self.call, 'component_id'), (self.result, 'component_id'),
                         (self.call, 'contract_version'), (self.result, 'contract_version'),
                         (self.result, 'run_id'), (self.result, 'as_of')]:
            with self.subTest(key=key):
                saved = obj[key]
                obj[key] = '2.0.0' if key == 'contract_version' else ('2026-11-11T12:00:00Z' if key == 'as_of' else 'different')
                self.rejects(); obj[key] = saved

    def test_named_required_optional_and_unknown_ports(self):
        removed = self.call['inputs'].pop('task'); self.rejects()
        self.manifest['inputs'][0]['required'] = False; self.check()
        self.call['inputs']['undeclared'] = removed; self.rejects()

    def test_duplicate_declarations(self):
        for key in ('inputs', 'outputs', 'errors'):
            self.manifest[key].append(copy.deepcopy(self.manifest[key][0]))
            self.rejects(); self.manifest[key].pop()

    def test_binding_schema_must_match_approved_manifest(self):
        self.call['inputs']['task']['schema_sha256'] = '0' * 64; self.rejects()

    def test_invalid_payload_is_rejected_even_with_correct_hash(self):
        binding = self.call['inputs']['task']; data = b'{}'
        self.artifacts[binding['artifact']['ref']] = data
        binding['artifact']['sha256'] = cc.digest(data)
        self.rejects()

    def test_source_and_supersession_bytes_are_required(self):
        source = self.call['inputs']['task']['sources'][0]
        source['artifact'] = {'ref': 'fixture://missing-source', 'sha256': '0' * 64}; self.rejects()
        source['artifact'] = self.call['inputs']['task']['artifact']
        source['supersedes'] = {'ref': 'fixture://missing-prior', 'sha256': '0' * 64}; self.rejects()

    def test_input_fingerprint_and_method_must_match(self):
        self.result['provenance']['input_sha256'] = '0' * 64; self.rejects()
        self.result['provenance']['input_sha256'] = self.fingerprint
        self.result['provenance']['method'] = {'ref': 'other', 'sha256': '0' * 64}; self.rejects()

    def test_typed_failure_has_no_outputs_and_matches_declared_error(self):
        self.result.update(status='insufficient_evidence', outputs={},
                           error=dict(code='missing_evidence', message='Fixture unavailable', retryable=False))
        self.check()
        self.result['error']['retryable'] = True; self.rejects()
        self.result['error']['retryable'] = False
        self.result['error']['code'] = 'undeclared'; self.rejects()

    def test_strict_dates_do_not_depend_on_optional_packages(self):
        for stamp in ['2026-02-31T00:00:00Z', '2026-11-10T12:00:00+01:99', '2026-11-10']:
            self.call['as_of'] = stamp; self.rejects()
        self.call['as_of'] = self.result['as_of'] = '2026-11-10T07:00:00-05:00'; self.check()

    def test_legacy_manifest_remains_schema_valid_but_needs_pins_for_helper(self):
        del self.manifest['boundary_profile']; self.rejects()

    def test_self_contained_schema_policy_and_strict_json(self):
        for schema in [{'$ref': 'https://example.invalid/schema'},
                       {'$dynamicRef': 'file:///tmp/schema'},
                       {'$schema': 'http://json-schema.org/draft-07/schema#'}]:
            with self.assertRaises(cc.ConformanceError): cc._local_schema(schema)
        for data in [b'{"a":1,"a":2}', b'NaN', b'Infinity', b'1e999']:
            with self.assertRaises(cc.ConformanceError): cc._json(data)
        cc._validate({'x': 1}, {'$defs': {'number': {'type': 'number'}},
                               'properties': {'x': {'$ref': '#/$defs/number'}}})

    def test_schema_metadata_in_literal_data_is_not_a_reference(self):
        value = {'$ref': 'https://example.invalid/data', '$schema': 'literal'}
        for schema in [{'const': value}, {'enum': [value]}, {'default': value}]:
            cc._local_schema(schema)
            cc._validate(value, schema)
        for schema in [{'properties': {'x': {'$ref': 'https://example.invalid/schema'}}},
                       {'allOf': [{'$dynamicRef': 'file:///tmp/schema'}]}]:
            with self.assertRaises(cc.ConformanceError): cc._local_schema(schema)

    def test_conformance_is_not_market_qualification(self):
        # The helper deliberately does not turn descriptive unit/time/access
        # declarations or a placeholder code SHA into domain qualification.
        source = self.call['inputs']['task']['sources'][0]
        source.update(unit='unverified_unit', available_at='2027-01-01T00:00:00Z',
                      entitlement='unknown')
        self.check()


if __name__ == '__main__':
    unittest.main()
