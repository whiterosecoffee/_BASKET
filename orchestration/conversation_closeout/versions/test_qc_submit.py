import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from orchestration.conversation_closeout.versions.qc_intake import enqueue, verify_artifacts
from orchestration.conversation_closeout.versions.qc_submit import (
    build_request, committed_reader, main, write_request)
from orchestration.conversation_closeout.versions.test_qc_intake import index, sample


PREFIX = 'orchestration/conversation_closeout/versions/'
PRIMARY = PREFIX + 'primary.md'
HANDOFF = PREFIX + 'handoff.md'
OUTPUT = PREFIX + 'request.json'
BYTES = {PRIMARY: b'Primary evidence\n', HANDOFF: b'O1: obligation\nK1: knowledge\n'}


def request(task=None, revision='a' * 40, items=('O1', 'K1'), reader=None, primary=None):
    return build_request(task or sample()['task'], 179, revision,
                         primary or [PRIMARY], HANDOFF, items,
                         reader or (lambda path, rev: BYTES[path]))


class QcSubmitTests(unittest.TestCase):
    def test_existing_intake_consumes_request_and_replay_is_noop(self):
        result = request()
        self.assertTrue(verify_artifacts(result, lambda path, rev: BYTES[path]))
        first = enqueue(index(), result)
        self.assertEqual(first, enqueue(first, result))
        self.assertEqual(len(first['requests']), 1)

    def test_request_is_deterministic_and_does_not_mutate_task(self):
        task = sample()['task']; original = copy.deepcopy(task)
        self.assertEqual(request(task=task), request(task=task, items=('K1', 'O1')))
        self.assertEqual(task, original)
        for artifact in request()['artifacts']:
            self.assertEqual(artifact['sha256'], hashlib.sha256(BYTES[artifact['path']]).hexdigest())

    def test_changed_source_bytes_change_identity(self):
        reader = lambda path, rev: BYTES[path] + (b'new evidence\n' if path == PRIMARY else b'')
        self.assertNotEqual(request()['request_id'], request(reader=reader)['request_id'])

    def test_unsafe_unowned_and_unpinned_inputs_reject_before_reads(self):
        def forbidden(*args):
            self.fail('invalid request reached artifact reader')
        for kwargs in ({'primary': ['../outside']}, {'primary': ['tickers/X/entity.json']},
                       {'revision': 'HEAD'}, {'revision': 'a' * 7}, {'items': ('O1', 'O1')}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                request(reader=forbidden, **kwargs)

    def test_missing_inventory_and_duplicate_handoff_rejected(self):
        with self.assertRaisesRegex(ValueError, 'IDs differ'):
            request(items=('O1',))
        with self.assertRaisesRegex(ValueError, 'duplicate handoff'):
            request(reader=lambda p, r: BYTES[p] + (b'O1: repeated\n' if p == HANDOFF else b''))

    def test_bad_or_missing_source_rejected(self):
        with self.assertRaisesRegex(ValueError, 'return bytes'):
            request(reader=lambda p, r: 'not bytes')
        with self.assertRaises(UnicodeDecodeError):
            request(reader=lambda p, r: b'\xff')
        with self.assertRaises(FileNotFoundError):
            request(reader=lambda p, r: (_ for _ in ()).throw(FileNotFoundError(p)))

    def test_output_create_replay_and_conflicting_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / PREFIX).mkdir(parents=True)
            self.assertEqual(write_request(root, OUTPUT, request()), 'created')
            before = (root / OUTPUT).stat().st_mtime_ns
            self.assertEqual(write_request(root, OUTPUT, request()), 'unchanged')
            self.assertEqual((root / OUTPUT).stat().st_mtime_ns, before)
            with self.assertRaisesRegex(ValueError, 'different content'):
                write_request(root, OUTPUT, request(revision='b' * 40))

    def test_output_rejects_escapes_unowned_queue_archive_and_missing_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            for output in ('../escape', '/tmp/escape', 'README.md', PREFIX + '../escape',
                           PREFIX + 'QC_QUEUE.json', PREFIX + 'qc_archive/id.json',
                           PREFIX + 'missing/request.json'):
                with self.subTest(output=output), self.assertRaises(ValueError):
                    write_request(tmp, output, request())

    def test_output_rejects_symlink_even_when_destination_stays_in_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / PREFIX).mkdir(parents=True)
            (root / PREFIX / 'other').mkdir()
            (root / PREFIX / 'link').symlink_to(root / PREFIX / 'other', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                write_request(root, PREFIX + 'link/request.json', request())
            (root / OUTPUT).symlink_to(root / PREFIX / 'other.json')
            with self.assertRaisesRegex(ValueError, 'symlink'):
                write_request(root, OUTPUT, request())

    def make_repo(self, root):
        def git(*args):
            return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL).decode().strip()
        git('init', '-q'); git('config', 'user.name', 'Local test'); git('config', 'user.email', 'test@example.invalid')
        for path, data in BYTES.items():
            dest = root / path; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
        git('add', '.'); git('commit', '-qm', 'test fixture')
        return git

    def test_real_git_reader_uses_commit_not_dirty_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); git = self.make_repo(root); sha = git('rev-parse', 'HEAD')
            (root / PRIMARY).write_text('uncommitted overwrite')
            result = request(revision=sha, reader=committed_reader(root, sha))
            self.assertTrue(verify_artifacts(result, lambda p, r: BYTES[p]))
            for bad in ('HEAD', 'a' * 40, git('rev-parse', 'HEAD:' + PRIMARY)):
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    committed_reader(root, bad)
            with self.assertRaisesRegex(ValueError, 'differs from pinned'):
                committed_reader(root, sha)(PRIMARY, 'HEAD')

    def test_missing_git_artifact_does_not_fall_back_to_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); git = self.make_repo(root); sha = git('rev-parse', 'HEAD')
            (root / PREFIX / 'uncommitted.md').write_text('not committed')
            with self.assertRaisesRegex(ValueError, 'not a regular committed file'):
                request(revision=sha, primary=[PREFIX + 'uncommitted.md'], reader=committed_reader(root, sha))

    def test_source_symlink_is_not_treated_as_primary_file_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); git = self.make_repo(root)
            (root / PREFIX / 'link.md').symlink_to('primary.md')
            git('add', '.'); git('commit', '-qm', 'symlink fixture')
            sha = git('rev-parse', 'HEAD')
            with self.assertRaisesRegex(ValueError, 'not a regular committed file'):
                request(revision=sha, primary=[PREFIX + 'link.md'], reader=committed_reader(root, sha))

    def test_cli_writes_request_but_never_claims_submission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); git = self.make_repo(root); sha = git('rev-parse', 'HEAD')
            task = root / 'task.json'; task.write_text(json.dumps(sample()['task']))
            args = ['--source-repo', str(root), '--task', str(task), '--source-pr', '179',
                    '--revision', sha, '--primary', PRIMARY, '--handoff', HANDOFF,
                    '--item-id', 'O1', '--item-id', 'K1', '--output', OUTPUT]
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(main(args), 0)
            receipt = json.loads(stdout.getvalue())
            self.assertFalse(receipt['submitted']); self.assertFalse(receipt['accepted'])
            result = json.loads((root / OUTPUT).read_text())
            self.assertEqual(receipt['request_id'], result['request_id'])
            self.assertEqual(enqueue(index(), result)['requests'], [result])
            self.assertFalse((root / PREFIX / 'QC_QUEUE.json').exists())
            args[args.index('--revision') + 1] = 'HEAD'
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                self.assertEqual(main(args), 2)
            self.assertFalse(json.loads(stderr.getvalue())['submitted'])


if __name__ == '__main__':
    unittest.main()
