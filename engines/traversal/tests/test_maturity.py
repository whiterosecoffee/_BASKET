"""Local validation of the experimental B06 projection, not a system schema.

No network, provider invocation, raw-data reads, or production calculations.
Source-byte validation requires the pinned Git objects retrieved during intake.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[3]
PACKET = ROOT / 'engines/traversal/maturity.json'
SOURCE_REPOSITORY = Path(os.environ.get('B06_SOURCE_REPOSITORY', str(ROOT))).resolve()
DIMENSIONS = {'proposed', 'implemented', 'tested', 'independently_accepted',
              'published', 'integrated', 'operational'}
EVIDENCE_KINDS = {
    'tested': {'test_report', 'independent_test_report'},
    'independently_accepted': {'independent_test_report', 'independent_acceptance'},
    'integrated': {'integration_report'},
    'operational': {'operational_report'},
}
GATE_PROOF_KINDS = {'test_report', 'independent_test_report', 'independent_acceptance',
                    'integration_report', 'operational_report', 'qualification_report'}


def nodes(root):
    yield root
    for child in root['children']:
        yield from nodes(child)


def gates(items):
    for item in items:
        yield item
        yield from gates(item['children'])


def ready(node):
    """Mandatory gates cannot be masked by a passing ancestor or sibling."""
    return all(g['status'] == 'pass' for n in nodes(node)
               for g in gates(n['acceptance']) if g['mandatory'])


def validate(packet):
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    require(packet['status'] == 'experimental_domain_projection', 'experimental status')
    require(packet['format'] == 'b06.experimental-domain-projection@0.1', 'format')
    sources, evidence = packet['sources'], packet['evidence']
    for key, source in sources.items():
        require(re.fullmatch(r'[0-9a-f]{40}', source['revision']), 'source revision')
        require(re.fullmatch(r'[0-9a-f]{64}', source['sha256']), 'source digest')
        require(source['url'].endswith(source['revision']+'/'+source['path']), 'source locator')
    for item in evidence.values():
        require(item['source'] in sources, 'unknown source')
        require(item['source_revision'] == sources[item['source']]['revision'], 'wrong source revision')
        require(bool(item['locator']), 'missing locator')
    ns = list(nodes(packet['objective']))
    identifiers = [n['id'] for n in ns] + [n['id'] for n in packet['external_owners']]
    require(len(set(identifiers)) == len(identifiers), 'duplicate node ID')
    gate_ids = []
    for n in ns:
        for field in ('id','purpose','outcome','owner','branch','scope','next_action'):
            require(bool(n[field]), 'missing node '+field)
        require(set(n['status']) == DIMENSIONS, 'missing status dimension')
        require(all(s in sources for s in n['source_refs']), 'unknown node source')
        require(all(d in identifiers for d in n['dependencies']), 'unknown dependency')
        for dimension, claim in n['status'].items():
            require(claim['state'] in ('established','not_claimed'), 'invalid claim state')
            require(all(e in evidence for e in claim['evidence']), 'unknown evidence')
            if claim['state'] == 'established':
                require(bool(claim['evidence']), 'missing evidence')
                require(not n['ghost'] or dimension == 'proposed', 'ghost promotion')
                if dimension != 'proposed':
                    require(all(evidence[e]['source'] in n['source_refs'] for e in claim['evidence']),
                            'evidence belongs to another node source')
                if dimension in EVIDENCE_KINDS:
                    require(any(evidence[e]['kind'] in EVIDENCE_KINDS[dimension]
                                for e in claim['evidence']), 'wrong proof class')
                    require(all(evidence[e].get('result') == 'pass' for e in claim['evidence']),
                            'nonpassing proof')
            else:
                require(not claim['evidence'], 'evidence attached to unclaimed dimension')
        for g in gates(n['acceptance']):
            gate_ids.append(g['id'])
            require(g['status'] in ('pass','fail','blocked','not_run'), 'invalid gate status')
            require(isinstance(g['mandatory'], bool), 'mandatory flag')
            require(all(e in evidence for e in g['evidence']), 'unknown gate evidence')
            if g['status'] == 'pass':
                require(bool(g['evidence']), 'missing gate evidence')
                require(all(c['status'] == 'pass' for c in gates(g['children']) if c['mandatory']),
                        'nested mandatory gate masking')
                require(any(evidence[e]['kind'] in GATE_PROOF_KINDS
                            and evidence[e].get('result') == 'pass'
                            and g['id'] in evidence[e].get('criterion_ids', [])
                            for e in g['evidence']), 'missing exact-criterion passing proof')
                require(not any(evidence[e].get('result') in ('fail', 'blocked', 'not_run', 'skipped')
                                for e in g['evidence']), 'contradictory gate proof')
        require(n['readiness'] in ('ready','blocked','not_assessed'), 'readiness')
        if n['readiness'] == 'ready':
            require(not n['ghost'], 'ghost readiness')
            require(ready(n), 'mandatory gate masking')
    require(len(gate_ids) == len(set(gate_ids)), 'duplicate gate ID')
    for edge in packet['relationships']:
        require(edge['from_id'] in identifiers and edge['to_id'] in identifiers, 'dangling relationship')
        require(edge['type'] in {'contains','requires','reuses','specified_by','informed_by','optional_context',
                                'discoverable_through','contract_review_by','execution_pattern_by',
                                'independent_acceptance_by','provides_to'}, 'relationship type')
    require(not packet['fetch_receipt']['coverage_qualified'], 'placement promoted to coverage')
    require(not packet['fetch_receipt']['current_input_qualified'], 'placement promoted to current input')
    if 'adapter_specification' in packet:
        spec = packet['adapter_specification']
        require(spec['status'] == 'proposed' and spec['implemented'] is False, 'adapter promotion')
        require(spec['execution_gate']['status'] == 'blocked', 'adapter execution gate')
        require(all(s in sources for s in spec['source_refs']), 'unknown adapter source')
        require(all(case['result'] == 'not_run' and not case['evidence']
                    for case in spec['acceptance_cases']), 'planned adapter case promoted')
    return True


class MaturityTests(unittest.TestCase):
    def setUp(self):
        self.p = json.loads(PACKET.read_text(encoding='utf-8'))

    def test_packet(self):
        self.assertTrue(validate(self.p))
        self.assertFalse(ready(self.p['objective']))

    def test_exact_source_bytes(self):
        # Git reads only: disable lazy fetch to make a missing pin a failure.
        env = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0')
        for key, s in self.p['sources'].items():
            with self.subTest(source=key):
                data = subprocess.check_output(['git','show',s['revision']+':'+s['path']], cwd=SOURCE_REPOSITORY, env=env)
                self.assertEqual(hashlib.sha256(data).hexdigest(), s['sha256'])

    def test_reject_ghost_promotion(self):
        ghost = next(n for n in nodes(self.p['objective']) if n['ghost'])
        ghost['status']['implemented'] = dict(state='established', evidence=['metrics_read'])
        with self.assertRaisesRegex(ValueError, 'ghost promotion'):
            validate(self.p)

    def test_reject_missing_evidence(self):
        observed = next(n for n in nodes(self.p['objective']) if n['id'] == 'B06.RANGES.OBSERVED')
        observed['status']['tested']['evidence'] = []
        with self.assertRaisesRegex(ValueError, 'missing evidence'):
            validate(self.p)

    def test_reject_wrong_source_revision(self):
        self.p['evidence']['metrics_independent']['source_revision'] = self.p['evidence']['metrics_independent']['runner_revision']
        with self.assertRaisesRegex(ValueError, 'wrong source revision'):
            validate(self.p)

    def test_reject_nested_mandatory_masking(self):
        outer = self.p['objective']['acceptance'][0]
        outer.update(status='pass', evidence=['metrics_independent'])
        outer['children'][0]['status'] = 'fail'
        with self.assertRaisesRegex(ValueError, 'nested mandatory gate masking'):
            validate(self.p)

    def test_reject_parent_ready_with_blocked_descendant(self):
        self.p['objective']['readiness'] = 'ready'
        with self.assertRaisesRegex(ValueError, 'mandatory gate masking'):
            validate(self.p)

    def test_reject_source_read_as_test(self):
        observed = next(n for n in nodes(self.p['objective']) if n['id'] == 'B06.RANGES.OBSERVED')
        observed['status']['tested']['evidence'] = ['metrics_read']
        with self.assertRaisesRegex(ValueError, 'wrong proof class'):
            validate(self.p)

    def test_reject_placement_as_coverage(self):
        self.p['fetch_receipt']['coverage_qualified'] = True
        with self.assertRaisesRegex(ValueError, 'placement promoted'):
            validate(self.p)

    def test_historical_current_and_consumer_are_separate(self):
        by_id = {n['id']:n for n in nodes(self.p['objective'])}
        self.assertNotEqual(by_id['B06.INPUT.HISTORICAL']['acceptance'], by_id['B06.INPUT.CURRENT']['acceptance'])
        self.assertIn('EXT.TRAJECTORY', by_id['B06.DELIVERY.LOCAL']['dependencies'])
        self.assertEqual(self.p['user_replay_request']['status'], 'awaiting_timestamp_resolution_and_qualified_inputs')

    def test_reject_failed_test_as_established(self):
        self.p['evidence']['metrics_independent']['result'] = 'fail'
        with self.assertRaisesRegex(ValueError, 'nonpassing proof'):
            validate(self.p)

    def test_reject_other_component_test_evidence(self):
        observed = next(n for n in nodes(self.p['objective']) if n['id'] == 'B06.RANGES.OBSERVED')
        observed['status']['tested']['evidence'] = ['geometry_tests']
        with self.assertRaisesRegex(ValueError, 'another node source'):
            validate(self.p)

    def test_reject_ghost_ready_even_without_gates(self):
        ghost = next(n for n in nodes(self.p['objective']) if n['ghost'])
        ghost['acceptance'] = []
        ghost['children'] = []
        ghost['readiness'] = 'ready'
        with self.assertRaisesRegex(ValueError, 'ghost readiness'):
            validate(self.p)

    def test_reject_planned_adapter_case_as_executed(self):
        self.p['adapter_specification']['acceptance_cases'][0]['result'] = 'pass'
        with self.assertRaisesRegex(ValueError, 'planned adapter case promoted'):
            validate(self.p)

    def test_reject_adapter_implementation_claim(self):
        self.p['adapter_specification']['implemented'] = True
        with self.assertRaisesRegex(ValueError, 'adapter promotion'):
            validate(self.p)

    def test_reject_source_inspection_as_gate_proof(self):
        observed = next(n for n in nodes(self.p['objective']) if n['id'] == 'B06.RANGES.OBSERVED')
        observed['acceptance'][0].update(status='pass', evidence=['metrics_read'])
        observed['readiness'] = 'ready'
        with self.assertRaisesRegex(ValueError, 'exact-criterion passing proof'):
            validate(self.p)

    def test_reject_unrelated_passing_test_as_gate_proof(self):
        observed = next(n for n in nodes(self.p['objective']) if n['id'] == 'B06.RANGES.OBSERVED')
        observed['acceptance'][0].update(status='pass', evidence=['metrics_independent'])
        with self.assertRaisesRegex(ValueError, 'exact-criterion passing proof'):
            validate(self.p)

    def test_accept_exact_criterion_proof_shape(self):
        # Synthetic metadata tests only, never written back as real acceptance.
        observed = next(n for n in nodes(self.p['objective']) if n['id'] == 'B06.RANGES.OBSERVED')
        gate = observed['acceptance'][0]
        self.p['evidence']['synthetic_qualification'] = dict(
            source='metrics', source_revision=self.p['sources']['metrics']['revision'],
            kind='qualification_report', result='pass', criterion_ids=[gate['id']],
            locator='synthetic-fixture:shape-only')
        gate.update(status='pass', evidence=['synthetic_qualification'])
        self.assertTrue(validate(self.p))
        self.assertFalse(ready(self.p['objective']))

    def test_reject_conflicting_gate_proof(self):
        observed = next(n for n in nodes(self.p['objective']) if n['id'] == 'B06.RANGES.OBSERVED')
        gate = observed['acceptance'][0]
        for name, result in [('synthetic_pass','pass'), ('synthetic_fail','fail')]:
            self.p['evidence'][name] = dict(
                source='metrics', source_revision=self.p['sources']['metrics']['revision'],
                kind='qualification_report', result=result, criterion_ids=[gate['id']],
                locator='synthetic-fixture:shape-only')
        gate.update(status='pass', evidence=['synthetic_pass','synthetic_fail'])
        with self.assertRaisesRegex(ValueError, 'contradictory gate proof'):
            validate(self.p)


if __name__ == '__main__':
    unittest.main()
