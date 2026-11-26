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
def local(ref):
    path = (ROOT / '_MAP' / ref.split('#', 1)[0]).resolve()
    assert path.is_relative_to((ROOT / '_MAP').resolve())
    return path

def reference(ref):
    value = load(local(ref))
    if '#' in ref:
        fragment = ref.split('#', 1)[1]
        assert fragment.startswith('/')
        for part in fragment[1:].split('/'):
            part = part.replace('~1', '/').replace('~0', '~')
            value = value[int(part)] if isinstance(value, list) else value[part]
    return value

def evidence_check(ref):
    evidence = reference(ref)
    assert evidence['experiment_files']
    for name, expected in evidence['experiment_files'].items():
        target = (local(ref).parent / name).resolve()
        assert target.is_relative_to(local(ref).parent)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == expected
    return evidence

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
        assert group['coverage'] in {'partial', 'complete'}
        if group['coverage'] == 'partial':
            assert group['gap']
        else:
            assert not group['gap']
            closure = evidence_check(group['coverage_evidence_ref'])
            assert closure['group_id'] == group['id'] and closure['remaining_gaps'] == []
            inventory = reference(group['inventory_ref'])
            assert inventory['group_id'] == group['id']
            assert inventory['required_requirement_ids'] and set(inventory['required_requirement_ids']) == set(closure['verified_requirement_ids'])
            assert closure['inventory_sha256'] == hashlib.sha256(local(group['inventory_ref']).read_bytes()).hexdigest()
            assert closure['independent_review']['accepted'] is True
            assert closure['independent_review']['source_url'].startswith('https://')
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
        assert node['mapping_state'] in {'unmapped', 'partial', 'mapped'}
        if node['mapping_state'] == 'unmapped':
            assert node['inputs'] is None and node['outputs'] is None and node['binding'] is None
            assert node['remaining_gaps']
        else:
            assert isinstance(node['binding'], dict)
            for port in ('inputs', 'outputs'):
                assert isinstance(node[port], dict)
                jsonschema.Draft202012Validator.check_schema(reference(node[port]['schema_ref']))
            contract = reference(node['binding']['contract_ref'])
            evidence = evidence_check(node['binding']['evidence_ref'])
            boundary = contract['definitions'][node['binding']['root_definition']]
            base = Path(node['binding']['contract_ref']).parent
            for port, definition_port in (('inputs', 'input'), ('outputs', 'output')):
                assert node[port]['schema_ref'] == str(base / boundary[definition_port])
            assert node['binding']['scope'] and node['binding']['requirement_ids']
            requirements = {q['id']: q for q in contract['requirements']}
            assert len(requirements) == len(contract['requirements'])
            assert set(node['binding']['requirement_ids']) <= set(requirements)
            assert set(node['binding']['requirement_ids']) <= set(evidence['requirements_covered'])
            cases = {c['id'] for c in evidence['results']}
            for requirement in requirements.values():
                assert requirement['cases'] and set(requirement['cases']) <= cases
            assert bool(node['remaining_gaps']) == (node['mapping_state'] == 'partial')
            if node['mapping_state'] == 'mapped':
                inventory = reference(node['domain_inventory_ref'])
                closure = evidence_check(node['closure_evidence_ref'])
                assert inventory['domain_id'] == closure['domain_id'] == node['id']
                assert inventory['scope'] == closure['scope'] == 'full_catalog_domain'
                assert inventory['catalog_commit'] == catalog_ref['commit']
                assert inventory['required_requirement_ids']
                assert set(inventory['required_requirement_ids']) == set(closure['verified_requirement_ids'])
                assert closure['inventory_sha256'] == hashlib.sha256(local(node['domain_inventory_ref']).read_bytes()).hexdigest()
                assert closure['independent_review']['accepted'] is True
                assert closure['independent_review']['source_url'].startswith('https://')
    assert doc['queue_contract']['runtime_status'] == 'specified_not_implemented'
    assert doc['queue_contract']['authority_issue'] == 136
    queue = doc['queue_contract']
    for field in ('read', 'proposal_fields', 'write', 'reject', 'validation_needed'):
        assert isinstance(queue[field], list) and queue[field]
        assert all(isinstance(x, str) and x.strip() for x in queue[field])
    assert {'expected_updated_at_and_body_hash', 'idempotency_key', 'minimal_delta', 'preserved_obligations', 'evidence_urls', 'next_owner_action'} <= set(queue['proposal_fields'])
    for field in ('reader', 'writer'):
        assert isinstance(queue[field], str) and queue[field].strip()
    assert doc['owner']['write_paths'] == ['_MAP/**', 'orchestration/tests/test_map_suite_discovery.py']
    amendment = reference(doc['owner']['scope_amendment'])
    assert amendment['scope'] == doc['owner']['write_paths']
    assert amendment['collision_check']['overlapping_prs'] == []
    pins = reference('source_pins.json')['commits']
    assert len(pins) == len(set(pins))
    assert set(pins) == {source['commit'] for source in doc['sources'].values()}
    if doc['coverage']['complete']:
        assert all(g['coverage'] == 'complete' for g in doc['groups'])
        assert all(n['mapping_state'] == 'mapped' for n in doc['domains'])
        closure = evidence_check(doc['coverage']['closure_evidence_ref'])
        assert closure['source_inventory_complete'] is True and closure['remaining_gaps'] == []
    archive_ids = [c['id'] for c in doc['archive_microtests']['cases']]
    assert archive_ids and len(archive_ids) == len(set(archive_ids))
    for case in doc['archive_microtests']['cases']:
        assert case['archive_pointer'] in doc['sources']
        assert case['execution'] in {'not_run', 'executed_offline_microtest'}
        if case['execution'] == 'executed_offline_microtest':
            evidence = load(ROOT / '_MAP' / case['evidence_ref'])
            assert evidence['evidence_class'] == 'executed_offline_microtest'
            directory = (ROOT / '_MAP' / case['evidence_ref']).parent
            for name, digest in evidence['experiment_files'].items():
                assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
        assert case['difference_class'] in {'preserve_required_behavior', 'intended_correction', 'irrelevant_legacy_behavior', 'unresolved'}
    assert doc['instruction_semantics']['examples'][0]['disposition'] == 'replace'
    queue_evidence = load(ROOT / '_MAP' / doc['queue_contract']['offline_experiment']['evidence'])
    assert queue_evidence['external_effects'] == 0
    queue_cases = load(local('microtests/queue_handoff/cases.json'))['cases']
    assert len({c['id'] for c in queue_cases}) == len(queue_cases)
    assert len({c['id'] for c in queue_evidence['cases']}) == len(queue_evidence['cases'])
    assert {c['id'] for c in queue_cases} == {c['id'] for c in queue_evidence['cases']}
    for name, digest in queue_evidence['experiment_files'].items():
        assert hashlib.sha256((ROOT / '_MAP/microtests/queue_handoff' / name).read_bytes()).hexdigest() == digest
    suites = reference(doc['coverage']['suite_manifest'])['suites']
    assert suites and len({s['id'] for s in suites}) == len(suites)
    declared_evidence = {s['evidence'] for s in suites}
    assert all(c['evidence_ref'] in declared_evidence for c in doc['archive_microtests']['cases'] if c['execution'] == 'executed_offline_microtest')
    assert doc['queue_contract']['offline_experiment']['evidence'] in declared_evidence
    assert all(n['binding']['evidence_ref'] in declared_evidence for n in doc['domains'] if n['mapping_state'] != 'unmapped')
    for suite in suites:
        assert local(suite['runner']).is_file()
        cases = reference(suite['cases'])['cases']
        evidence = evidence_check(suite['evidence'])
        results = evidence[suite['results_key']]
        assert evidence['evidence_class'] == suite['evidence_class']
        assert len({c['id'] for c in cases}) == len(cases)
        assert len({c['id'] for c in results}) == len(results)
        assert {c['id'] for c in cases} == {c['id'] for c in results}

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
    bad = copy.deepcopy(document); bad['domains'][0]['mapping_state'] = 'mapped'; bad['domains'][0]['remaining_gaps'] = []; mutations.append(bad)
    bad = copy.deepcopy(document); bad['coverage']['complete'] = True; mutations.append(bad)
    bad = copy.deepcopy(document); bad['domains'][1]['mapping_state'] = 'mapped'; mutations.append(bad)
    bad = copy.deepcopy(document); bad['domains'][0]['binding']['evidence_ref'] = 'missing.json'; mutations.append(bad)
    for bad in mutations:
        try:
            validate(bad)
        except (AssertionError, KeyError, FileNotFoundError, jsonschema.ValidationError):
            continue
        raise AssertionError('review regression accepted')
    print('PASS: shape, pinned sources, unique group/pattern/domain references, required queue field presence; maturation and false-completeness rejection cases. Freshness, semantic-boundary and queue evidence are bounded offline microtests, not production or autonomous execution.')
