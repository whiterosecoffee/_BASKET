"""Validate the prior-art projection; not an external standard implementation."""
import copy
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def resolve(ref):
    name,_,pointer=ref.partition('#')
    p=(ROOT/name).resolve()
    assert p.is_relative_to(ROOT) and p.is_file()
    value=json.loads(p.read_text())
    if pointer:
        assert pointer.startswith('/')
        for part in pointer[1:].split('/'):
            part=part.replace('~1','/').replace('~0','~')
            value=value[int(part)] if isinstance(value,list) else value[part]
    return value

def validate(d):
    assert d['format']=='basket.map.prior_art_families@1'
    families={f['id']:f for f in d['families']}
    assert len(families)==len(d['families'])
    for f in families.values():
        assert f['decision'] in ('adopt','adapt','reject')
        assert f['source']['url'].startswith('https://') and f['source']['claim']
        assert f['application'] and f['rejected_scope'] and f['map_refs']
        for ref in f['map_refs']:resolve(ref)
    objects={o['id']:o for o in d['objects']}
    assert len(objects)==len(d['objects'])
    for o in objects.values():
        assert o['family'] in families
        value=resolve(o['ref'])
        assert o['kind'] in ('definition','instance','contract','evidence','requirement','plan')
        if 'expected_id' in o:assert value['id']==o['expected_id']
        if o['kind']=='evidence':assert o['execution_scope']=='offline_reference'
    endpoints={'instance_of':('instance','definition'),'input_contract':('definition','contract'),'has_evidence':('requirement','evidence'),'declares':('plan','definition')}
    for e in d['relations']:
        source=objects[e['from']];target=objects[e['to']]
        left=resolve(source['ref']);right=resolve(target['ref'])
        if e['kind']=='instance_of':
            assert left['definition']==target['ref'].rsplit('/',1)[1]
        elif e['kind']=='input_contract':
            name,_,fragment=left['input'].partition('#')
            resolved=(Path(source['ref'].partition('#')[0]).parent/name).as_posix()+'#'+fragment
            assert resolved==target['ref']
        elif e['kind']=='has_evidence':
            assert left['id'] in right['requirements_covered']
            assert set(left['cases']) <= {r['id'] for r in right['results']}
        assert (objects[e['from']]['kind'],objects[e['to']]['kind'])==endpoints[e['kind']]
    for example in d['examples']:
        assert example['path'] and all(x in objects for x in example['path']) and example['limit']

def main():
    d=json.loads((HERE/'families.json').read_text());validate(d)
    mutations={}
    def bad(name):
        v=copy.deepcopy(d);mutations[name]=v;return v
    bad('duplicate_family')['families'].append(copy.deepcopy(d['families'][0]))
    del bad('missing_source')['families'][0]['source']
    bad('dangling_pointer')['objects'][0]['ref']='system.json#/does_not_exist'
    bad('unknown_family')['objects'][0]['family']='absent'
    bad('dangling_edge')['relations'][0]['to']='absent'
    bad('wrong_endpoint_kind')['relations'][0]['to']='request_shape'
    bad('false_production_evidence')['objects'][3]['execution_scope']='production'
    bad('unknown_relation')['relations'][0]['kind']='executes'
    bad('instance_pointer_drift')['objects'][1]['ref']='compositions/admission/composition.json#/instances/3'
    bad('contract_pointer_drift')['objects'][2]['ref']='compositions/admission/schemas.json#/$defs/report'
    bad('evidence_pointer_drift')['objects'][3]['ref']='microtests/freshness/evidence.json'
    results=[{'id':'valid_projection','result':'accepted'}]
    for name,mutant in mutations.items():
        try:validate(mutant)
        except (AssertionError,KeyError,IndexError,ValueError,FileNotFoundError):results.append({'id':name,'result':'rejected'})
        else:raise AssertionError(name)
    assert {r['id'] for r in results}=={c['id'] for c in json.loads((HERE/'cases.json').read_text())['cases']}
    print(json.dumps({'evidence_class':'executed_offline_projection_checks','results':results,'external_effects':0,'production_qualified':False},indent=2))
if __name__=='__main__':main()
