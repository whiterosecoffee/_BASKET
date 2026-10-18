"""Guard mandatory CI commands against accidental omission and optional skips."""
import copy
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]
VALIDATORS = ('versions', 'sparks', 'goals', 'planner', 'worker_scopes', 'worker_attempts')
QC_COMMANDS = tuple('python orchestration/validate_' + name + '.py' for name in VALIDATORS) + (
    "python -m unittest discover -s orchestration/tests -p 'test_*.py' -v",
    'python orchestration/worker_protocol.py --task orchestration/examples/B05.task.json --resolution orchestration/examples/B05.resolution.json --evidence orchestration/examples/github-evidence-2026-10-16.json',
    "python -m unittest discover -s tests/integration -p 'test_*.py' -v",
)
STORE_COMMANDS = (
    "python -m unittest discover -s tests/integration -p 'test_relationship*.py' -v",
    'python tests/validate_stores.py',
)


def contract_errors(doc):
    errors = []
    # PyYAML uses YAML 1.1, where GitHub's unquoted 'on' becomes True.
    triggers = doc.get('on', doc.get(True, {}))
    if triggers != {'push': {'branches': ['main']}, 'pull_request': None}:
        errors.append('main push and every PR must validate; avoid feature push duplicates')
    if doc.get('concurrency') != {
        'group': '${{ github.workflow }}-${{ github.event_name }}-${{ github.event.pull_request.number || github.ref }}',
        'cancel-in-progress': "${{ github.event_name == 'pull_request' }}",
    }:
        errors.append('concurrency must isolate workflow/event/PR and never cancel main')
    jobs = doc.get('jobs', {})
    for name, commands in (('stores', STORE_COMMANDS), ('worker-qc', QC_COMMANDS)):
        job = jobs.get(name, {})
        if 'if' in job or job.get('continue-on-error'):
            errors.append(name + ' job may be skipped or ignored')
        for command in commands:
            matches = [s for s in job.get('steps', []) if s.get('run') == command]
            if len(matches) != 1:
                errors.append('missing/duplicate mandatory command: ' + command)
            elif matches[0].get('if') != '${{ !cancelled() }}' or matches[0].get('continue-on-error'):
                errors.append('mandatory command can be hidden: ' + command)
        checkout = [s for s in job.get('steps', []) if s.get('uses') == 'actions/checkout@v4']
        if len(checkout) != 1 or checkout[0].get('with', {}).get('ref') != '${{ github.event.pull_request.head.sha || github.sha }}':
            errors.append('test exact PR head: ' + name)
    gate = jobs.get('validate', {})
    if set(gate.get('needs', [])) != {'stores', 'worker-qc'} or gate.get('if') != '${{ always() }}':
        errors.append('aggregate must require both jobs even on failure')
    steps = gate.get('steps', [])
    if len(steps) != 1 or steps[0].get('run') != 'test "$STORES" = success && test "$WORKER_QC" = success':
        errors.append('aggregate must reject every non-success result')
    elif steps[0].get('env') != {'STORES': '${{ needs.stores.result }}', 'WORKER_QC': '${{ needs.worker-qc.result }}'}:
        errors.append('aggregate must use actual dependency results')
    return errors


class CIContract(unittest.TestCase):
    def setUp(self):
        self.doc = yaml.safe_load((ROOT / '.github/workflows/validate.yml').read_text())

    def test_required_workflow_contract(self):
        self.assertEqual(contract_errors(self.doc), [])

    def test_feature_push_duplicates_rejected(self):
        self.doc[True]['push'] = None
        self.assertTrue(contract_errors(self.doc))

    def test_cross_pr_cancellation_rejected(self):
        self.doc['concurrency']['group'] = '${{ github.workflow }}'
        self.assertTrue(contract_errors(self.doc))

    def test_main_cancellation_rejected(self):
        self.doc['concurrency']['cancel-in-progress'] = True
        self.assertTrue(contract_errors(self.doc))

    def test_missing_each_gate_rejected(self):
        for command in QC_COMMANDS:
            with self.subTest(command=command):
                altered = copy.deepcopy(self.doc)
                steps = altered['jobs']['worker-qc']['steps']
                steps[:] = [s for s in steps if s.get('run') != command]
                self.assertTrue(contract_errors(altered))

    def test_optional_script_skip_rejected(self):
        altered = copy.deepcopy(self.doc)
        step = next(s for s in altered['jobs']['worker-qc']['steps'] if s.get('run') == QC_COMMANDS[0])
        step['if'] = "${{ hashFiles('orchestration/validate_versions.py') != '' }}"
        self.assertTrue(contract_errors(altered))

    def test_masked_failure_rejected(self):
        altered = copy.deepcopy(self.doc)
        next(s for s in altered['jobs']['worker-qc']['steps'] if s.get('run') == QC_COMMANDS[0])['continue-on-error'] = True
        self.assertTrue(contract_errors(altered))

    def test_wrong_checkout_revision_rejected(self):
        self.doc['jobs']['worker-qc']['steps'][0]['with']['ref'] = 'main'
        self.assertTrue(contract_errors(self.doc))

    def test_skipped_dependency_cannot_be_accepted(self):
        self.doc['jobs']['validate']['needs'] = ['stores']
        self.assertTrue(contract_errors(self.doc))


if __name__ == '__main__':
    unittest.main()
