"""Regressions for #66: old source refs must not supply acceptance code."""
import fnmatch
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]


class OpenAIWorkflowHotfix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = yaml.load(
            (ROOT / '.github/workflows/openai-research.yml').read_text(),
            Loader=yaml.BaseLoader,
        )
        cls.steps = cls.workflow['jobs']['openai-research']['steps']
        cls.runner = next(s['run'] for s in cls.steps if s.get('name') == 'Independent B01 fail-closed checks')

    def test_acceptance_checkout_is_workflow_revision_not_old_source_head(self):
        checkouts = {s['with']['path']: s['with']['ref'] for s in self.steps if s.get('uses') == 'actions/checkout@v4'}
        self.assertEqual(checkouts['acceptance'], '${{ github.workflow_sha }}')
        self.assertEqual(checkouts['gate'], '${{ github.event.pull_request.head.sha || github.sha }}')
        self.assertEqual(checkouts['source'], '${{ steps.research-source.outputs.sha }}')
        self.assertNotIn('gate/tests', self.runner)
        verification = next(s for s in self.steps if s.get('name') == 'Record both exact revisions and require complete research')
        self.assertIn('git -C acceptance rev-parse HEAD', verification['run'])
        self.assertIn('EXPECTED_ACCEPTANCE', verification['run'])

    def test_unrelated_changes_and_duplicate_branch_pushes_are_filtered(self):
        triggers = self.workflow['on']
        self.assertEqual(triggers['push']['branches'], ['main'])
        for event in ('push', 'pull_request'):
            patterns = triggers[event]['paths']
            self.assertTrue(any(fnmatch.fnmatch('research/OPENAI/ipo2027.py', p) for p in patterns))
            self.assertFalse(any(fnmatch.fnmatch('orchestration/agentic/manager.py', p) for p in patterns))
        self.assertIn('workflow_dispatch', triggers)
        self.assertEqual(self.workflow['concurrency']['cancel-in-progress'], "${{ github.event_name == 'pull_request' }}")

    def run_fixture(self, text):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Reproduce the incident: the actual source checkout has no B01 suite.
            (root / 'gate/tests/integration').mkdir(parents=True)
            acceptance = root / 'acceptance/tests/integration'
            acceptance.mkdir(parents=True)
            if text is not None:
                (acceptance / 'openai_research_acceptance.py').write_text(text)
            return subprocess.run(['bash', '-e', '-c', self.runner], cwd=root,
                                  capture_output=True, text=True, timeout=15)

    def test_old_source_without_acceptance_executes_independent_suite(self):
        result = self.run_fixture('import unittest\nclass Gate(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Ran 1 test', result.stderr)

    def test_missing_acceptance_fails(self):
        self.assertNotEqual(self.run_fixture(None).returncode, 0)

    def test_empty_acceptance_fails(self):
        result = self.run_fixture('# No tests\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Empty acceptance suite', result.stderr)

    def test_skipped_acceptance_fails(self):
        result = self.run_fixture('import unittest\nclass Gate(unittest.TestCase):\n @unittest.skip("missing dependency")\n def test_skip(self): pass\n')
        self.assertNotEqual(result.returncode, 0)

    def test_failing_acceptance_fails(self):
        result = self.run_fixture('import unittest\nclass Gate(unittest.TestCase):\n def test_fail(self): self.fail("real failure")\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('real failure', result.stderr)
