"""Verify a bounded connector export, then execute its explicitly named tests.

This complements B01's full-checkout domain_source_gate; it does not replace it.
Only run source already authorized for local execution. Hashes are integrity
checks, not a hostile-code sandbox or proof of manifest authorship.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_sync_gate import revision, strict_result


def load_manifest(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    if set(value) != {'schema', 'source_revision', 'component', 'files', 'modules', 'minimum'}:
        raise ValueError('exact manifest fields required')
    if value['schema'] != 'basket.component_export_review@0.1-draft':
        raise ValueError('unsupported draft manifest')
    revision(value['source_revision'])
    def safe_path(name):
        if type(name) is not str or not name or '\\' in name:
            return False
        p = PurePosixPath(name)
        return not p.is_absolute() and str(p) == name and '..' not in p.parts
    component = value['component']
    if not safe_path(component):
        raise ValueError('unsafe component path')
    if type(value['files']) is not dict or not value['files']:
        raise ValueError('nonempty file inventory required')
    for name, blob in value['files'].items():
        if not safe_path(name) or not name.startswith(component + '/'):
            raise ValueError('file outside component')
        revision(blob)
    modules = value['modules']
    if type(modules) is not list or not modules or any(type(m) is not str for m in modules) or len(set(modules)) != len(modules):
        raise ValueError('unique named modules required')
    for module in modules:
        if type(module) is not str or re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*', module) is None or module.replace('.', '/') + '.py' not in value['files']:
            raise ValueError('test module not in verified inventory')
    if type(value['minimum']) is not int or value['minimum'] <= 0:
        raise ValueError('positive test minimum required')
    return value


def fingerprint(root, manifest):
    root = Path(root).resolve()
    actual = {}
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('symlink in component export')
        if path.is_file():
            name = path.relative_to(root).as_posix()
            if name not in manifest['files']:
                raise ValueError('unexpected export input: ' + name)
            data = path.read_bytes()
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            if blob != manifest['files'][name]:
                raise ValueError('Git blob mismatch: ' + name)
            actual[name] = hashlib.sha256(data).hexdigest()
    if set(actual) != set(manifest['files']):
        raise ValueError('missing export input')
    return actual


def child(source, manifest_path, result_path):
    manifest = load_manifest(manifest_path)
    fingerprint(source, manifest)
    os.chdir(source)
    sys.path.insert(0, str(source))
    suite = unittest.defaultTestLoader.loadTestsFromNames(manifest['modules'])
    count = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    packet = dict(discovered=count, run=result.testsRun, minimum=manifest['minimum'],
                  failures=len(result.failures), errors=len(result.errors),
                  skipped=len(result.skipped), expected_failures=len(result.expectedFailures),
                  unexpected_successes=len(result.unexpectedSuccesses),
                  passed=bool(strict_result(count, result, manifest['minimum'])))
    result_path.write_text(json.dumps(packet, indent=2) + '\n')
    return 0 if packet['passed'] else 1


def run(source, manifest_path, output, timeout=60):
    source, manifest_path, output = source.resolve(), manifest_path.resolve(), output.resolve()
    tool = Path(__file__).resolve()
    helper = tool.parents[1] / 'project_sync_gate.py'
    if not source.is_dir() or output.is_relative_to(source) or output == manifest_path or manifest_path.is_relative_to(output):
        raise ValueError('evidence must be outside source and manifest')
    if type(timeout) not in (int, float) or not 0 < timeout <= 300:
        raise ValueError('bounded positive timeout required')
    output.mkdir(parents=True, exist_ok=False)
    packet = dict(schema='basket.component_export_result@0.1-draft', passed=False,
                  verification_scope='component_export_only', semantic_acceptance=False,
                  integrated=False, operational=False)
    try:
        manifest = load_manifest(manifest_path)
        raw_manifest = manifest_path.read_bytes()
        before = fingerprint(source, manifest)
        reviewers = {str(p.name): hashlib.sha256(p.read_bytes()).hexdigest() for p in (tool, helper)}
        packet.update(source_revision=manifest['source_revision'],
                      manifest_sha256=hashlib.sha256(raw_manifest).hexdigest(),
                      reviewer_files=reviewers, files=before, modules=manifest['modules'])
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / 'result.json'
            frozen = Path(directory) / 'manifest.json'
            frozen.write_bytes(raw_manifest)
            command = [sys.executable, str(tool), '--child', '--source', str(source),
                       '--manifest', str(frozen), '--output', str(result_path)]
            # Reduce accidental local import contamination; this is not isolation.
            environment = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME'}}
            environment['PYTHONDONTWRITEBYTECODE'] = '1'
            with (output / 'suite.log').open('w') as log:
                completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                                           env=environment, timeout=timeout)
            packet['exit_code'] = completed.returncode
            if result_path.exists():
                packet['tests'] = json.loads(result_path.read_text())
        packet['inputs_unchanged'] = (fingerprint(source, manifest) == before
            and manifest_path.read_bytes() == raw_manifest
            and all(hashlib.sha256(p.read_bytes()).hexdigest() == reviewers[p.name] for p in (tool, helper)))
        packet['passed'] = bool(completed.returncode == 0 and packet.get('tests', {}).get('passed') is True and packet['inputs_unchanged'])
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        packet['error'] = str(exc)
    (output / 'evidence.json').write_text(json.dumps(packet, sort_keys=True, indent=2) + '\n')
    return packet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--timeout', type=float, default=60)
    parser.add_argument('--child', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child:
        return child(args.source.resolve(), args.manifest, args.output)
    try:
        packet = run(args.source, args.manifest, args.output, args.timeout)
    except (OSError, ValueError) as exc:
        print(json.dumps({'passed': False, 'error': str(exc)}))
        return 2
    print(json.dumps(packet, sort_keys=True, indent=2))
    return 0 if packet['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
