"""Disposable scheduled-delivery harness. No scheduler installation or dispatch."""
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import re
import tempfile
import time
import json

from .core import digest, require
from . import github_readonly
from .synthetic_adapter import load_json, shape

SCHEMA = 'basket.handoff_dry_run_checkpoint@0.1-draft'


def identifier(value):
    require(type(value) is str and re.fullmatch('[A-Za-z0-9][A-Za-z0-9._-]{0,63}', value) is not None, 'invalid bounded identifier')


def implementation():
    return {name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ('dry_run.py', 'github_readonly.py')}


def decision(observation, prior_ids):
    if observation['observation_id'] in prior_ids:
        return 'dry-run-no-source-change'
    if observation['pr']['state'] != 'open':
        return 'dry-run-park'
    ci = observation['ci']
    if ci['availability'] != 'available' or ci['complete'] is not True:
        return 'dry-run-request-evidence'
    if any(run['status'] != 'completed' for run in ci['runs']):
        return 'dry-run-wait-ci'
    if any(run['conclusion'] != 'success' for run in ci['runs']):
        return 'dry-run-review-failure'
    return 'dry-run-review-next-step'


def validate_checkpoint(state):
    shape(state, 'schema disposable harness_id head implementation revision receipts')
    require(state['schema'] == SCHEMA and state['disposable'] is True, 'disposable checkpoint required')
    identifier(state['harness_id'])
    github_readonly.endpoints(state['head'])
    require(state['implementation'] == implementation(), 'implementation changed; create a new disposable checkpoint')
    require(type(state['revision']) is int and type(state['receipts']) is list and state['revision'] == len(state['receipts']), 'receipt count/revision mismatch')
    seen, observations, previous = set(), [], None
    for index, receipt in enumerate(state['receipts'], 1):
        shape(receipt, 'receipt_id sequence wake wake_digest previous_receipt input_checkpoint_digest implementation source_mode observation decision dispatch_authorized actual_scheduled_execution recorded_at')
        validate_wake(receipt['wake'], state['head'])
        require(receipt['wake']['id'] not in seen, 'duplicate durable wake')
        seen.add(receipt['wake']['id'])
        require(receipt['sequence'] == index and receipt['previous_receipt'] == previous, 'receipt chain mismatch')
        predecessor = dict(state, revision=index-1, receipts=state['receipts'][:index-1])
        require(receipt['input_checkpoint_digest'] == digest(predecessor), 'predecessor checkpoint digest mismatch')
        require(receipt['implementation'] == state['implementation'], 'receipt implementation mismatch')
        require(receipt['wake_digest'] == digest(receipt['wake']), 'wake content mismatch')
        require(receipt['dispatch_authorized'] is False and receipt['actual_scheduled_execution'] is False, 'dry-run authority only')
        require(receipt['source_mode'] in ('supplied', 'actual-readonly-gh'), 'unsupported source mode')
        observation = receipt['observation']
        require(observation['subject']['revision'] == state['head'] and observation['execution_authorized'] is False and observation['reviewer_acceptance'] is False, 'receipt subject/authority mismatch')
        require(receipt['decision'] == decision(observation, observations), 'decision mismatch')
        require(github_readonly.finite(receipt['recorded_at']), 'invalid receipt time')
        payload = {k:v for k,v in receipt.items() if k != 'receipt_id'}
        require(receipt['receipt_id'] == digest(payload), 'receipt digest mismatch')
        observations.append(observation['observation_id'])
        previous = receipt['receipt_id']


def validate_wake(wake, head):
    shape(wake, 'id head scheduled_for')
    identifier(wake['id'])
    require(wake['head'] == head, 'wake revision mismatch')
    require(github_readonly.finite(wake['scheduled_for']), 'invalid wake timestamp')


def _atomic_write(path, value):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
            temporary = stream.name
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
        require(load_json(path.read_text(encoding='utf-8')) == value, 'readback mismatch; reread before retry')
    finally:
        if temporary is not None:
            os.unlink(temporary)


def initialize(path, *, harness_id, head):
    """Explicitly create NEW disposable state only; never migrate an old file."""
    state = dict(schema=SCHEMA, disposable=True, harness_id=harness_id, head=head,
                 implementation=implementation(), revision=0, receipts=[])
    validate_checkpoint(state)
    path = Path(path)
    lock = path.with_suffix(path.suffix + '.lock')
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.close(fd)
        require(not path.exists(), 'checkpoint already exists')
        _atomic_write(path, state)
        return state
    finally:
        os.unlink(lock)


def _deliver(path, wake, expected_digest, clock, reader, source_mode):
    path = Path(path)
    lock = path.with_suffix(path.suffix + '.lock')
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.close(fd)
        current = load_json(path.read_text(encoding='utf-8'))
        validate_checkpoint(current)
        validate_wake(wake, current['head'])
        for receipt in current['receipts']:
            if receipt['wake']['id'] == wake['id']:
                require(receipt['wake_digest'] == digest(wake), 'wake key reused with different content')
                return dict(delivery='replayed', effective_decisions=0, receipt=deepcopy(receipt), dispatch_authorized=False)
        require(digest(current) == expected_digest, 'checkpoint CAS conflict')
        now = clock()
        require(github_readonly.finite(now) and 0 <= now - wake['scheduled_for'] <= 300, 'stale/future wake')
        responses, failure = reader(current['head'])
        require(failure is None, 'source unavailable; no receipt committed')
        checked_at = clock()
        require(github_readonly.finite(checked_at) and 0 <= checked_at - wake['scheduled_for'] <= 300, 'wake expired during retrieval')
        observation = github_readonly.normalize_supplied(responses, head=current['head'], now=checked_at)
        # The input normalizer never authenticates payloads. This separate mode
        # records which harness port was used, without granting source authority.
        prior_ids = [r['observation']['observation_id'] for r in current['receipts']]
        payload = dict(sequence=current['revision']+1, wake=deepcopy(wake), wake_digest=digest(wake),
                       previous_receipt=current['receipts'][-1]['receipt_id'] if current['receipts'] else None,
                       input_checkpoint_digest=digest(current), implementation=current['implementation'],
                       source_mode=source_mode, observation=observation, decision=decision(observation, prior_ids),
                       dispatch_authorized=False, actual_scheduled_execution=False, recorded_at=checked_at)
        receipt = dict(payload, receipt_id=digest(payload))
        updated = deepcopy(current)
        updated['revision'] += 1
        updated['receipts'].append(receipt)
        validate_checkpoint(updated)
        _atomic_write(path, updated)
        return dict(delivery='recorded', effective_decisions=1, receipt=receipt, dispatch_authorized=False)
    finally:
        os.unlink(lock)


def deliver_supplied(path, wake, responses, *, expected_digest, now):
    """Deterministic simulated scheduler delivery; supplied source data only."""
    return _deliver(path, wake, expected_digest, lambda:now, lambda head:(responses,None), 'supplied')


def deliver_readonly(path, wake, *, expected_digest):
    """Simulated delivery with actual GET retrieval, never actual scheduled work."""
    return _deliver(path, wake, expected_digest, time.time, github_readonly._read_responses, 'actual-readonly-gh')
