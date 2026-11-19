"""Read-only qualification of pinned #230 model; no recovery implementation.

Run from repo root with PYTHONDONTWRITEBYTECODE=1. Requires the pinned map Git
object locally (git fetch origin 1a9fdb7952676d026e92d001f88f62de67f103e0).
Emits JSON to stdout; no network, journal writes, or worker execution.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PIN = '1a9fdb7952676d026e92d001f88f62de67f103e0'
PREFIX = '_MAP/microtests/queue_handoff/'

def blob(path):
    return subprocess.check_output(['git', 'show', PIN + ':' + PREFIX + path], cwd=ROOT)

def run():
    raw = {name: blob(name) for name in ('contract.json', 'cases.json', 'run.py')}
    contract = json.loads(raw['contract.json'])
    fixtures = json.loads(raw['cases.json'])
    # Verify actual imported helpers against the reference's pinned byte hashes.
    for ref in contract['archive_sources']:
        assert hashlib.sha256((ROOT / ref['path']).read_bytes()).hexdigest() == ref['sha256'], ref['path']
    from orchestration.worker_bridge import bridge
    from orchestration.agentic import manager
    namespace = {'__file__': str(ROOT / PREFIX / 'run.py'), '__name__': 'qualification_reference'}
    exec(compile(raw['run.py'], PREFIX + 'run.py', 'exec'), namespace)
    experiment = namespace['experiment']
    before = copy.deepcopy(fixtures)
    baseline = []
    for case in fixtures['cases']:
        result = experiment(bridge, manager, fixtures, case)
        assert result['outcome'] == case['expected_outcome'], case['id']
        assert result['next_proposal'] == case['expected_next'], case['id']
        assert result['external_effects'] == 0
        baseline.append({'id': case['id'], 'outcome': result['outcome']})
    byid = {c['id']: c for c in fixtures['cases']}
    definitions = [
        ('untrusted_provenance', 'uncertain_matching', {'observation_provenance': {'verified': False, 'origin': 'caller_claim'}}, 'next_proposal', 'Provenance not consumed; digest equality is not target authentication.'),
        ('revoked_authority', 'uncertain_matching', {'current_authorization': 'revoked'}, 'next_proposal', 'Post-readback authorization not consumed.'),
        ('newer_steering', 'uncertain_matching', {'steering': {'dispatch_revision': 'r1', 'current_revision': 'r2', 'conflicts': True}}, 'next_proposal', 'Current steering revision not consumed.'),
        ('absent_in_flight', 'uncertain_absent', {'original_request': {'state': 'in_flight', 'fenced': False}}, 'retry_requires_fresh_authority_and_state', 'No next proposal/effect; in-flight distinction not represented.'),
        ('absent_terminal', 'uncertain_absent', {'original_request': {'state': 'terminal_no_effect', 'fenced': True}}, 'retry_requires_fresh_authority_and_state', 'Same conservative result; terminal proof does not grant execution.'),
        ('wrong_target', 'uncertain_matching', {}, 'write_conflict', 'Existing envelope comparison rejects a different target even with recomputed digest.')
    ]
    observations = []
    for name, parent, extension, expected, finding in definitions:
        case = copy.deepcopy(byid[parent])
        case.update(extension)
        # Preserve existing variant selector; these are extra-contract probes.
        if name == 'wrong_target':
            value = case['readback']['result']
            value['envelope']['target_scope'] = 'other-synthetic-target'
            value['sha256'] = hashlib.sha256(json.dumps(value['envelope'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        saved = copy.deepcopy(case)
        result = experiment(bridge, manager, fixtures, case)
        assert result['outcome'] == expected, name
        assert result['external_effects'] == 0
        assert experiment(bridge, manager, fixtures, case) == result, name
        assert case == saved and fixtures == before, name
        observations.append({'id': name, 'base_case': parent, 'extra_contract_inputs': extension, 'mutation': 'target_scope changed and digest recomputed' if name == 'wrong_target' else None, 'observed': result, 'finding': finding})
    return {'classification': 'actual_offline_characterization_not_operational_acceptance', 'map_revision': PIN, 'helper_revision': contract['archive_commit'], 'source_sha256': {k: hashlib.sha256(v).hexdigest() for k,v in raw.items()}, 'baseline_cases': baseline, 'probes': observations, 'case_count': len(baseline)+len(observations), 'failures': 0, 'external_effects': 0, 'unchanged_replay': True, 'interpretation': 'Unsupported extra fields are ignored by this bounded model. This demonstrates a qualification boundary, not a claimed violation of its existing declared contract. No real authorization or target trust was verified.', 'next_owner_action': '#230 adopt/defer provenance, in-flight and post-readback authority inputs before #32/#78 implementation allocation.'}

if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
