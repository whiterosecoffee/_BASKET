"""Independent negative coverage for exact-source CI; no Project or network calls."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('project_sync_gate', Path(__file__).with_name('project_sync_gate.py'))
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class ProjectSyncGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.acceptance = self.root / 'acceptance'
        for directory in (self.source, self.acceptance):
            directory.mkdir()
            (directory / 'README').write_text('fixture only\n')
            self.git(directory, 'init', '-b', 'main')
            self.commit(directory)
        self.output = self.root / 'evidence'

    def git(self, root, *args):
        return subprocess.check_output(['git', '-c', 'user.name=Gate fixture', '-c',
            'user.email=gate@example.invalid', '-C', str(root), *args], stderr=subprocess.DEVNULL,
            text=True).strip()

    def commit(self, root):
        self.git(root, 'add', '.')
        self.git(root, 'commit', '-m', 'Fixture')
        return self.git(root, 'rev-parse', 'HEAD')

    def suite(self, body='pass', count=88, decorator=''):
        directory = self.source / 'orchestration/project_sync'
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'test_fixture.py').write_text('import unittest\nfrom pathlib import Path\n'
            'import time\nclass Fixture(unittest.TestCase):\n' +
            ''.join(f'    {decorator}\n    def test_{i:03d}(self):\n        {body}\n' for i in range(count)) if count else '')
        return self.commit(self.source)

    def run_fixture(self, timeout=10):
        with contextlib.redirect_stdout(io.StringIO()):
            code = gate.run_gate(self.source, self.git(self.source, 'rev-parse', 'HEAD'),
                self.acceptance, self.git(self.acceptance, 'rev-parse', 'HEAD'), 'adapter',
                'actual_head', self.output, timeout=timeout)
        return code, json.loads((self.output / 'evidence.json').read_text())

    def test_full_sha_required(self):
        for value in ['main', 'abc', 'A'*40, 'f'*39, 'f'*40+'\n', '$(bad)']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                gate.revision(value)

    def test_absent_source_is_explicitly_labeled_pinned_dependency(self):
        self.assertEqual(gate.select(self.source), {'sha': gate.PINNED_SOURCE, 'mode': 'unmerged_dependency_only'})

    def test_partial_source_never_falls_back(self):
        (self.source / 'copier.yml').write_text('partial')
        sha = self.commit(self.source)
        self.assertEqual(gate.select(self.source), {'sha': sha, 'mode': 'actual_head'})

    def test_removed_source_never_falls_back(self):
        marker = self.source / 'copier.yml'
        marker.write_text('source existed')
        self.commit(self.source)
        marker.unlink()
        self.commit(self.source)
        with self.assertRaisesRegex(ValueError, 'removed'):
            gate.select(self.source)

    def test_absent_source_requires_complete_history(self):
        real_git = gate.git
        def shallow(root, *args):
            if args == ('rev-parse', '--is-shallow-repository'):
                return 'true'
            return real_git(root, *args)
        with patch.object(gate, 'git', side_effect=shallow), self.assertRaisesRegex(ValueError, 'Complete history'):
            gate.select(self.source)

    def test_explicit_source_is_validated(self):
        self.assertEqual(gate.select(self.source, 'a'*40)['mode'], 'explicit_exact_revision')
        with self.assertRaises(ValueError):
            gate.select(self.source, 'main')

    def test_fingerprint_rejects_wrong_revision(self):
        with self.assertRaises(ValueError):
            gate.fingerprint(self.source, 'a'*40)

    def test_fingerprint_rejects_dirty_and_untracked_inputs(self):
        sha = self.git(self.source, 'rev-parse', 'HEAD')
        (self.source / 'README').write_text('changed')
        with self.assertRaises(ValueError):
            gate.fingerprint(self.source, sha)
        self.git(self.source, 'checkout', '--', 'README')
        (self.source / 'untracked').write_text('unexpected')
        with self.assertRaises(ValueError):
            gate.fingerprint(self.source, sha)

    def test_missing_suite_fails(self):
        code, report = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertFalse(report['passed'])

    def test_empty_suite_fails(self):
        self.suite(count=0)
        self.assertEqual(self.run_fixture()[0], 1)

    def test_reduced_suite_fails(self):
        self.suite(count=1)
        code, report = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertEqual(report['result']['run'], 1)

    def test_complete_suite_passes_with_hash_and_counts(self):
        self.suite()
        code, report = self.run_fixture()
        self.assertEqual(code, 0)
        self.assertEqual(report['result']['run'], 88)
        self.assertEqual(report['result']['skipped'], 0)
        self.assertTrue(report['inputs_unchanged'])
        self.assertEqual(len(report['source_manifest_sha256']), 64)
        self.assertTrue((self.output / 'source-files.json').is_file())

    def test_skipped_suite_fails(self):
        self.suite(decorator='@unittest.skip("fixture")')
        code, report = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertEqual(report['result']['skipped'], 88)

    def test_expected_failure_suite_fails(self):
        self.suite(body='self.fail("fixture")', decorator='@unittest.expectedFailure')
        code, report = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertEqual(report['result']['expected_failures'], 88)

    def test_failing_suite_fails(self):
        self.suite(body='self.fail("fixture")')
        self.assertEqual(self.run_fixture()[0], 1)

    def test_import_error_fails(self):
        self.suite()
        (self.source / 'orchestration/project_sync/test_fixture.py').write_text('raise ImportError("fixture")')
        self.commit(self.source)
        self.assertEqual(self.run_fixture()[0], 1)

    def test_mutated_inputs_fail_after_passing_tests(self):
        self.suite(body='Path("README").write_text("mutated")')
        code, report = self.run_fixture()
        self.assertEqual(code, 1)
        self.assertIn('changed', report['error'])

    def test_timeout_fails_and_keeps_evidence(self):
        self.suite(body='time.sleep(1)')
        code, report = self.run_fixture(timeout=0.1)
        self.assertEqual(code, 1)
        self.assertIn('timed out', report['error'])
        self.assertTrue((self.output / 'suite.log').exists())

    def test_evidence_cannot_change_source_checkout(self):
        with self.assertRaises(ValueError):
            gate.run_gate(self.source, 'a'*40, self.acceptance, 'b'*40, 'adapter',
                          'actual_head', self.source / 'evidence')

    def test_workflow_is_readonly_and_has_named_suites(self):
        workflow = Path(__file__).resolve().parents[2] / '.github/workflows/project-sync-acceptance.yml'
        text = workflow.read_text()
        self.assertIn('suite: [adapter, copier]', text)
        self.assertIn('contents: read', text)
        self.assertIn('persist-credentials: false', text)
        self.assertIn('github.workflow_sha', text)
        self.assertIn('branches: [main]', text)
        self.assertNotIn('pull_request_target', text)
        self.assertNotIn('secrets.', text)
        self.assertNotIn('continue-on-error', text)
        self.assertIn('if-no-files-found: error', text)


if __name__ == '__main__':
    unittest.main()
