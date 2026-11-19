"""Offline negative probes of the pinned bridge; never launch a model.

The audit hook is a test tripwire, not a security boundary or runtime service.
A negative case passes only when the bridge rejects before any audited effect.
"""
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import replay

ACTIVE = False
ATTEMPTS = []
MUTATIONS = {'os.mkdir', 'os.remove', 'os.rename', 'os.rmdir', 'os.link',
             'os.symlink', 'os.chmod', 'os.chown', 'os.truncate', 'os.utime'}


class EffectAttempt(AssertionError):
    pass


def audit(event, args):
    if not ACTIVE:
        return
    forbidden = (event in MUTATIONS or event.startswith('subprocess.') or
                 event in {'os.system', 'os.fork', 'os.forkpty', 'os.posix_spawn', 'os.exec'} or
                 event.startswith('socket.'))
    if event == 'open':
        mode, flags = args[1:3]
        forbidden = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or bool(
            (flags or 0) & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
    if forbidden:
        ATTEMPTS.append(event)
        raise EffectAttempt(event)


sys.addaudithook(audit)


def pins():
    result = replay.verify_sources()
    for path, expected in replay.load('bridge-cases.json')['source_sha256'].items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('Pinned source mismatch: ' + path)
        result[path] = actual
    return result


def fixture(case_id):
    prepared = {'assignment': {'source_issue': 9001, 'execution': {
        'lease_id': 'lease-good', 'attempt_id': 'ATT-synthetic'}},
        'profile': {'capabilities': ['implementation']}}
    lease = {'schema': 'basket.agentic_event@1', 'event_id': 'lease-good',
             'type': 'lease_granted', 'task_id': 'T-9001', 'issue': 9001,
             'branch': 'work/9001-synthetic', 'at': '2026-01-01T00:00:00Z',
             'expires_at': '2026-01-01T02:00:00Z'}
    attempt = {'schema': 'basket.agentic_event@1', 'event_id': 'attempt-start',
               'type': 'attempt_started', 'task_id': 'T-9001',
               'attempt_id': 'ATT-synthetic', 'step_id': 'S1',
               'at': '2026-01-01T00:00:01Z'}
    events = [lease, attempt]
    output = ROOT / 'orchestration/worker_bridge/evidence/qualification-never-created'
    if case_id == 'readonly_write':
        prepared['profile']['capabilities'] = []
    elif case_id == 'outside_output':
        output = HERE / 'qualification-never-created'
    elif case_id == 'stale_token':
        prepared['assignment']['execution']['lease_id'] = 'lease-stale'
    elif case_id == 'expired_lease':
        lease['expires_at'] = '2026-01-01T00:30:00Z'
    elif case_id == 'missing_lease':
        events = [attempt]
    elif case_id == 'missing_attempt':
        events = [lease]
    elif case_id == 'wrong_attempt':
        prepared['assignment']['execution']['attempt_id'] = 'ATT-wrong'
    elif case_id == 'resolved_attempt':
        events.append(dict(attempt, event_id='attempt-end', type='attempt_passed',
                           at='2026-01-01T00:00:02Z', result_url='https://example.invalid/synthetic'))
    elif case_id != 'tripwire_control':
        raise ValueError('Unknown probe: ' + case_id)
    return prepared, events, output


def observe(case_id):
    global ACTIVE
    pins()  # Verify before importing the real implementations.
    from orchestration.worker_bridge import bridge
    from orchestration.agentic import manager
    prepared, events, output = fixture(case_id)
    original = copy.deepcopy((prepared, events))
    if output.exists():
        raise ValueError('Probe output path must not already exist')
    ATTEMPTS.clear()
    ACTIVE = True
    try:
        bridge.run_codex(ROOT, prepared, 'Synthetic qualification; never execute', output,
                         manager, events, dt.datetime(2026, 1, 1, 1, tzinfo=dt.timezone.utc))
        code = 'unexpected_return'
    except bridge.Blocked as error:
        code = error.code
    except EffectAttempt as error:
        code = 'effect_attempt:' + str(error)
    finally:
        ACTIVE = False
    return {'id': case_id, 'observed_code': code, 'effect_attempts': list(ATTEMPTS),
            'inputs_unchanged': original == (prepared, events), 'output_absent': not output.exists()}


def run():
    before = pins()
    corpus = replay.load('bridge-cases.json')
    results = []
    for case in corpus['cases']:
        result = observe(case['id'])
        result['expected_code'] = case['expected_code']
        result['passed'] = (result['observed_code'] == case['expected_code'] and
                            not result['effect_attempts'] and result['inputs_unchanged'] and
                            result['output_absent'])
        results.append(result)
    control = observe('tripwire_control')
    return {'entrypoint': corpus['entrypoint'], 'authority': corpus['authority'],
            'negative_cases': results, 'passed': sum(r['passed'] for r in results),
            'failed': sum(not r['passed'] for r in results),
            'tripwire_control': control, 'source_hashes': before,
            'unchanged_sources': before == pins(), 'limits': corpus['limits']}


if __name__ == '__main__':
    report = run()
    print(json.dumps(report, indent=2, sort_keys=True))
    control = report['tripwire_control']
    sys.exit(0 if not report['failed'] and report['unchanged_sources'] and
             control['observed_code'] == 'effect_attempt:os.mkdir' and
             control['effect_attempts'] == ['os.mkdir'] and control['output_absent'] else 1)
