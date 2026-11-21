"""B01 OpenAI CI utilities; evidence is run-local, never a task-state store."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def files(root):
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError('missing or symlinked input directory')
    result = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError('symlinked input: ' + str(p))
        if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc':
            result[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    if not result:
        raise ValueError('empty input directory')
    return result


def snapshot(source, acceptance, expected_source, expected_acceptance):
    result = {}
    for name, root, expected, relative in (
        ('source', Path(source), expected_source, 'research/OPENAI'),
        ('acceptance', Path(acceptance), expected_acceptance, 'tests/integration'),
    ):
        actual = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != expected or len(expected) != 40:
            raise ValueError('stale ' + name + ' revision')
        subprocess.run(['git', '-C', str(root), 'diff', '--exit-code', 'HEAD', '--', relative], check=True, capture_output=True)
        result[name] = {'sha': actual, 'files': files(root / relative)}
    result['python'] = sys.version
    result['dependency_fingerprint'] = digest(result)
    return result


def verify(before, after):
    if before != after:
        raise ValueError('inputs changed during validation; rerun from clean checkouts')


def suite(directory, pattern):
    tests = unittest.defaultTestLoader.discover(str(directory), pattern=pattern)
    if tests.countTestCases() == 0:
        raise ValueError('Empty source suite')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    return 0 if result.testsRun > 0 and result.wasSuccessful() and not result.skipped and not result.expectedFailures else 1


def bounded_suite(directory, pattern, timeout=120):
    try:
        return subprocess.run([sys.executable, str(Path(__file__).resolve()), 'suite-child', str(directory), pattern], timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        print('Source suite timeout; no automatic retry', file=sys.stderr)
        return 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    for mode in ('suite', 'suite-child'):
        q = sub.add_parser(mode)
        q.add_argument('directory')
        q.add_argument('pattern')
    q = sub.add_parser('snapshot')
    for arg in ('source', 'acceptance', 'source-sha', 'acceptance-sha', 'output'):
        q.add_argument('--' + arg, required=True)
    q.add_argument('--compare')
    a = p.parse_args(argv)
    try:
        if a.command == 'suite-child':
            return suite(a.directory, a.pattern)
        if a.command == 'suite':
            return bounded_suite(a.directory, a.pattern)
        output = Path(a.output)
        try:
            data = snapshot(a.source, a.acceptance, a.source_sha, a.acceptance_sha)
            if a.compare:
                verify(json.loads(Path(a.compare).read_text()), data)
            output.write_text(json.dumps(data, sort_keys=True, indent=2) + '\n')
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            output.write_text(json.dumps({'result': 'fail', 'error': str(error)}) + '\n')
            raise
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
