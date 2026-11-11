"""Offline shape and source checks only; no queue/network writes or workflow execution."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import jsonschema
ROOT = Path(__file__).resolve().parents[1]
def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=pairs)
def validate(doc):
    schema = load(ROOT / '_MAP/map.schema.json')
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(doc, schema)
    for path, source in doc['sources'].items():
        assert source['path'] == path
        raw = subprocess.check_output(['git', 'show', source['commit'] + ':' + path], cwd=ROOT)
        assert hashlib.sha256(raw).hexdigest() == source['sha256'], path
        assert source['url'].endswith('/' + source['commit'] + '/' + path)
    ids = {g['id'] for g in doc['groups']}
    assert ids == {f'G{i}' for i in range(1, 9)}
    assert len(doc['groups']) == len(ids)
    for group in doc['groups']:
        assert group['coverage'] == 'partial' and group['gap']
        assert all(ref in doc['sources'] for ref in group['source_refs'])
    assert len(doc['patterns']) == 7
    assert {p['id'] for p in doc['patterns']} == {f'P{i}' for i in range(1, 8)}
    for pattern in doc['patterns']:
        assert all(ref in doc['sources'] for ref in pattern['source_refs'])
    for edge in doc['relationships']:
        assert edge['from'] in ids | {'system'} and edge['to'] in ids
        assert edge['kind'] in {'contains', 'depends_on'}
    catalog_ref = doc['sources']['orchestration/sparks.json']
    catalog = json.loads(subprocess.check_output(['git', 'show', catalog_ref['commit'] + ':' + catalog_ref['path']], cwd=ROOT))
    assert len(doc['domains']) == len(catalog['sparks'])
    assert {n['id'] for n in doc['domains']} == {n['id'] for n in catalog['sparks']}
    assert {n['json_pointer'] for n in doc['domains']} == {f'/sparks/{i}' for i in range(len(catalog['sparks']))}
    for node in doc['domains']:
        assert node['source_ref'] == 'orchestration/sparks.json'
        assert node['source_ref'] in doc['sources']
        i = int(node['json_pointer'].split('/')[-1])
        assert catalog['sparks'][i]['id'] == node['id']
        assert node['inputs'] is None and node['outputs'] is None and node['binding'] is None
    assert doc['queue_contract']['runtime_status'] == 'specified_not_implemented'
    assert doc['queue_contract']['authority_issue'] == 136
    queue = doc['queue_contract']
    for field in ('read', 'proposal_fields', 'write', 'reject', 'validation_needed'):
        assert isinstance(queue[field], list) and queue[field]
        assert all(isinstance(x, str) and x.strip() for x in queue[field])
    assert {'expected_updated_at_and_body_hash', 'idempotency_key', 'minimal_delta', 'preserved_obligations', 'evidence_urls', 'next_owner_action'} <= set(queue['proposal_fields'])
    for field in ('reader', 'writer'):
        assert isinstance(queue[field], str) and queue[field].strip()
    assert doc['owner']['write_paths'] == ['_MAP/**']
    assert doc['coverage']['complete'] is False
    assert len(doc['archive_microtests']['cases']) == 4
    for case in doc['archive_microtests']['cases']:
        assert case['archive_pointer'] in doc['sources']
        assert case['execution'] in {'not_run', 'executed_offline_microtest'}
        if case['execution'] == 'executed_offline_microtest':
            assert case['id'] in {'AM1', 'AM2'}
            evidence = load(ROOT / '_MAP' / case['evidence_ref'])
            assert evidence['evidence_class'] == 'executed_offline_microtest'
            directory = (ROOT / '_MAP' / case['evidence_ref']).parent
            for name, digest in evidence['experiment_files'].items():
                assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
        assert case['difference_class'] in {'preserve_required_behavior', 'intended_correction', 'irrelevant_legacy_behavior', 'unresolved'}
    assert doc['instruction_semantics']['examples'][0]['disposition'] == 'replace'
    queue_evidence = load(ROOT / '_MAP' / doc['queue_contract']['offline_experiment']['evidence'])
    assert queue_evidence['external_effects'] == 0
    assert len(queue_evidence['cases']) == 12
    for name, digest in queue_evidence['experiment_files'].items():
        assert hashlib.sha256((ROOT / '_MAP/microtests/queue_handoff' / name).read_bytes()).hexdigest() == digest
if __name__ == '__main__':
    document = load(ROOT / '_MAP/system.json')
    validate(document)
    for field, value in [('status', 'operational'), ('format', 'unknown'), ('extra', True)]:
        bad = copy.deepcopy(document); bad[field] = value
        try:
            validate(bad)
        except (AssertionError, jsonschema.ValidationError):
            continue
        raise AssertionError('negative accepted: ' + field)
    bad = copy.deepcopy(document)
    next(iter(bad['sources'].values()))['sha256'] = '0' * 64
    try:
        validate(bad)
    except AssertionError:
        pass
    else:
        raise AssertionError('changed source accepted')
    mutations = []
    bad = copy.deepcopy(document); bad['domains'][-1] = copy.deepcopy(bad['domains'][0]); mutations.append(bad)
    bad = copy.deepcopy(document); bad['patterns'].append(copy.deepcopy(bad['patterns'][0])); mutations.append(bad)
    bad = copy.deepcopy(document); bad['domains'][0]['source_ref'] = 'nonexistent'; mutations.append(bad)
    bad = copy.deepcopy(document); bad['queue_contract'] = {'authority_issue': 136, 'runtime_status': 'specified_not_implemented'}; mutations.append(bad)
    for bad in mutations:
        try:
            validate(bad)
        except (AssertionError, KeyError, jsonschema.ValidationError):
            continue
        raise AssertionError('review regression accepted')
    print('PASS: shape, pinned sources, unique group/pattern/domain references, required queue field presence; 8 rejection cases. Freshness, semantic-boundary and queue evidence are bounded offline microtests, not production or autonomous execution.')
