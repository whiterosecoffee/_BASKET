"""B00 structural contract regressions. All fixtures are synthetic, not market evidence.

Reference contents and semantic predicates are deliberately not resolved by JSON
Schema. B01 and domain acceptance must verify them before execution qualification.
"""
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'schemas/component-blackbox.v1.json').read_text())
STAMP = '2026-11-10T12:00:00Z'
FORMAT_CHECKER = FormatChecker()


@FORMAT_CHECKER.checks('date-time', raises=ValueError)
def valid_datetime(value):
    # jsonschema without format extras silently omits its date-time checker.
    # Register explicitly so this suite cannot turn lexical shape into a pass.
    # This boundary profile uses timezone-aware timestamps without leap seconds.
    if not isinstance(value, str):
        return True
    offset = re.search(r'([+-])(\d{2}):(\d{2})$', value)
    if offset and (int(offset[2]) > 23 or int(offset[3]) > 59):
        return False
    parsed = datetime.fromisoformat(value.replace('t', 'T').replace('z', '+00:00').replace('Z', '+00:00'))
    return parsed.tzinfo is not None



def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def artifact(name='synthetic-fixture', value=None):
    return {'ref': 'fixture://' + name, 'sha256': hashlib.sha256(canonical(value or {'kind': 'synthetic_only'})).hexdigest()}


def source(**changes):
    result = dict(source_id='synthetic-source', artifact=artifact(), record_type='aggregate_bar',
                  subject_id='XNAS:EXAMPLE', observed_at=STAMP, available_at=STAMP,
                  ingested_at=STAMP, effective_at=STAMP, published_at=None,
                  period=None, session='RTH', unit='USD_per_share', currency='USD',
                  freshness='qualified', entitlement='not_required', supersedes=None)
    result.update(changes)
    return result


def binding(**source_changes):
    return dict(schema_ref='fixture://synthetic_payload.schema.json',
                schema_sha256=artifact('schema')['sha256'], artifact=artifact(),
                sources=[source(**source_changes)])


def manifest():
    port = dict(name='fixture', schema_ref='fixture://synthetic_payload.schema.json', required=True)
    return dict(schema='basket.component_contract@1', component_id='test.boundary', owner_spark='B00',
                version='1.0.0', determinism='pure', inputs=[copy.deepcopy(port)], outputs=[port],
                errors=[dict(code='missing_source', retryable=False)],
                acceptance=dict(test_command='python -m unittest', minimum_tests=1,
                                fixtures=['synthetic-fixture'], ci_owner='B01'))


def qualified_manifest():
    result = manifest()
    result.update(boundary_profile='qualified_refs_v1', assumptions=['Resolved input references'],
                  guarantees=['Typed fail-closed result'], effects=[])
    for port in result['inputs'] + result['outputs']:
        port.update(schema_sha256=artifact('schema')['sha256'], freshness_policy='point_in_time',
                    source_class='verified_observation')
    return result


def call():
    return dict(contract='basket.component_call@1', component_id='test.boundary', contract_version='1.0.0',
                run_id='synthetic-run', as_of=STAMP, inputs={'fixture': binding()},
                method=artifact('method'), options=dict(offline=True, seed=None))


def result(status='ok'):
    value = dict(contract='basket.component_result@1', component_id='test.boundary', contract_version='1.0.0',
                 run_id='synthetic-run', as_of=STAMP, status=status, outputs={'fixture': binding()},
                 provenance=dict(input_sha256=artifact()['sha256'], method=artifact('method'), code_sha='a'*40, generated_at=STAMP),
                 quality=dict(freshness='qualified', missing_inputs=[], conflicts=[], warnings=[]), error=None)
    if status != 'ok':
        value.update(outputs={}, error=dict(code='missing_source', message='Synthetic source is missing', retryable=False))
        value['quality'].update(freshness='unknown', missing_inputs=['fixture'])
    return value


def validator(definition=None):
    schema = SCHEMA if definition is None else {
        '$schema': SCHEMA['$schema'], '$defs': SCHEMA['$defs'], '$ref': '#/$defs/' + definition}
    return Draft202012Validator(schema, format_checker=FORMAT_CHECKER)


class ComponentBlackboxTests(unittest.TestCase):
    def valid(self, value, definition=None):
        validator(definition).validate(value)

    def invalid(self, value, definition=None):
        self.assertTrue(list(validator(definition).iter_errors(value)))

    def test_schema_is_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(SCHEMA)

    def test_legacy_manifest_is_unchanged_compatible(self):
        self.valid(manifest())

    def test_qualified_manifest_declares_boundary(self):
        self.valid(qualified_manifest())

    def test_qualified_manifest_requires_semantics_and_effects(self):
        for key in ('assumptions', 'guarantees', 'effects'):
            with self.subTest(key=key):
                value = qualified_manifest(); del value[key]; self.invalid(value)

    def test_qualified_ports_require_pins_and_policy(self):
        for direction in ('inputs', 'outputs'):
            for key in ('schema_sha256', 'freshness_policy', 'source_class'):
                with self.subTest(direction=direction, key=key):
                    value = qualified_manifest(); del value[direction][0][key]; self.invalid(value)

    def test_unknown_profile_is_not_silently_accepted(self):
        value = qualified_manifest(); value['boundary_profile'] = 'future'; self.invalid(value)

    def test_call_and_result_resolve_local_definitions(self):
        self.valid(call(), 'call'); self.valid(result(), 'result')

    def test_no_implicit_extra_fields(self):
        for definition, value in [('call', call()), ('result', result())]:
            value['undeclared_authority'] = True; self.invalid(value, definition)

    def test_call_requires_inputs(self):
        value = call(); value['inputs'] = {}; self.invalid(value, 'call')

    def test_bad_hash_rejected(self):
        value = call(); value['inputs']['fixture']['artifact']['sha256'] = 'not-external-evidence'; self.invalid(value, 'call')

    def test_malformed_timestamp_rejected_with_format_checker(self):
        value = call(); value['as_of'] = 'yesterday'; self.invalid(value, 'call')

    def test_date_without_timezone_is_not_datetime(self):
        value = call(); value['inputs']['fixture']['sources'][0]['observed_at'] = '2026-11-10'; self.invalid(value, 'call')

    def test_datetime_checker_is_installed_and_effective(self):
        self.assertIn('date-time', FORMAT_CHECKER.checkers)
        for stamp in ('2026-99-99T25:61:99Z', '2026-02-31T00:00:00Z',
                      '2026-11-10T12:00:00+99:99', '2026-11-10T12:00:60Z',
                      '2026-11-10T12:00:00+01:99', '2026-11-10T12:00:00+00:60'):
            with self.subTest(stamp=stamp):
                value = call(); value['as_of'] = stamp; self.invalid(value, 'call')
                value = result(); value['provenance']['generated_at'] = stamp; self.invalid(value, 'result')

    def test_datetime_valid_offset_and_null_policy(self):
        value = call(); value['as_of'] = '2026-11-10T07:00:00-05:00'
        self.valid(value, 'call')
        self.valid(source(effective_at=None, published_at=None), 'source_evidence')

    def test_unknown_time_preserved_not_qualified(self):
        value = call(); value['inputs']['fixture'] = binding(observed_at=None, available_at=None, freshness='unknown')
        self.valid(value, 'call')
        value['inputs']['fixture']['sources'][0]['freshness'] = 'qualified'; self.invalid(value, 'call')

    def test_stale_source_cannot_be_ok(self):
        value = result(); value['outputs']['fixture'] = binding(freshness='stale'); self.invalid(value, 'result')

    def test_unknown_source_cannot_be_ok(self):
        value = result(); value['outputs']['fixture'] = binding(freshness='unknown'); self.invalid(value, 'result')

    def test_unknown_or_denied_entitlement_cannot_be_ok(self):
        for entitlement in ('unknown', 'not_entitled'):
            value = result(); value['outputs']['fixture'] = binding(entitlement=entitlement); self.invalid(value, 'result')

    def test_ok_requires_output_and_sources(self):
        value = result(); value['outputs'] = {}; self.invalid(value, 'result')
        value = result(); value['outputs']['fixture']['sources'] = []; self.invalid(value, 'result')

    def test_ok_cannot_mask_missing_conflicting_or_stale_quality(self):
        for key, update in [('missing_inputs', ['x']), ('conflicts', ['x']), ('freshness', 'stale')]:
            value = result(); value['quality'][key] = update; self.invalid(value, 'result')

    def test_error_and_insufficient_evidence_require_typed_error(self):
        for status in ('error', 'insufficient_evidence'):
            value = result(status); self.valid(value, 'result')
            value['error'] = None; self.invalid(value, 'result')

    def test_unsuccessful_result_cannot_emit_success_payload(self):
        for status in ('error', 'insufficient_evidence'):
            value = result(status); value['outputs']['fixture'] = binding(); self.invalid(value, 'result')

    def test_ok_cannot_carry_error(self):
        value = result(); value['error'] = result('error')['error']; self.invalid(value, 'result')

    def test_revision_is_reference_not_overwrite(self):
        prior = artifact('prior', {'value': 1}); revised = artifact('revision', {'value': 2})
        value = source(artifact=revised, supersedes=prior)
        self.valid(value, 'source_evidence'); self.assertNotEqual(prior['sha256'], revised['sha256'])
        self.assertEqual(value['supersedes'], prior)

    def test_synthetic_replay_is_byte_and_hash_stable(self):
        value = call(); other = json.loads(json.dumps(value))
        self.assertEqual(canonical(value), canonical(other))
        self.assertEqual(hashlib.sha256(canonical(value)).digest(), hashlib.sha256(canonical(other)).digest())

    def test_record_types_do_not_conflate_options_and_bars(self):
        self.valid(binding(record_type='options_flow'), 'port_binding')
        self.valid(binding(record_type='macro_release', subject_id='US:CPI:HEADLINE', session='not_applicable', period='2026-10', unit='percent_yoy', currency=None), 'port_binding')
        self.invalid(binding(record_type='everything'), 'port_binding')

    def test_unit_compatibility_is_a_semantic_gate_not_schema_claim(self):
        # Both are structurally valid. A consumer requiring USD must reject the
        # JPY binding using its pinned payload/port contract, not this envelope.
        self.valid(binding(unit='JPY_per_share', currency='JPY'), 'port_binding')
        value = result('insufficient_evidence'); value['error']['code'] = 'incompatible_unit'
        self.valid(value, 'result')

    def test_schema_does_not_claim_content_or_temporal_verification(self):
        value = call(); value['inputs']['fixture']['artifact']['sha256'] = '0'*64
        value['inputs']['fixture']['sources'][0]['available_at'] = '2027-01-01T00:00:00Z'
        # Valid shape is not a valid reference or PIT snapshot. Independent
        # acceptance must resolve/check bytes and compare availability to as_of.
        self.valid(value, 'call')


if __name__ == '__main__':
    unittest.main()
