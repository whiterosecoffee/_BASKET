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
    assert {p['id'] for p in doc['patterns']} == {f'P{i}' for i in range(1, 8)}
    for pattern in doc['patterns']:
        assert all(ref in doc['sources'] for ref in pattern['source_refs'])
    for edge in doc['relationships']:
        assert edge['from'] in ids | {'system'} and edge['to'] in ids
        assert edge['kind'] in {'contains', 'depends_on'}
    catalog = load(ROOT / 'orchestration/sparks.json')
    assert len(doc['domains']) == len(catalog['sparks'])
    for node in doc['domains']:
        i = int(node['json_pointer'].split('/')[-1])
        assert catalog['sparks'][i]['id'] == node['id']
        assert node['inputs'] is None and node['outputs'] is None and node['binding'] is None
    assert doc['queue_contract']['runtime_status'] == 'specified_not_implemented'
    assert doc['queue_contract']['authority_issue'] == 136
    assert doc['owner']['write_paths'] == ['_MAP/**']
    assert doc['coverage']['complete'] is False
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
    print('PASS: shape, pinned source bytes, 8 groups, 7 patterns, 22 domain pointers, boundaries; 4 rejection cases')
