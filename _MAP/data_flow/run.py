"""Read pinned candidate JSON only; never execute the other owner's implementation."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
HERE=Path(__file__).resolve().parent
MAP=HERE.parent
ROOT=MAP.parent

def validate(d):
    assert d['state']=='candidate_reference_not_integrated'
    registry=json.loads((MAP/'system.json').read_text())['sources']
    loaded={}
    for name,source in d['sources'].items():
        assert source==registry[source['path']]
        raw=subprocess.check_output(['git','show',source['commit']+':'+source['path']],cwd=ROOT)
        assert hashlib.sha256(raw).hexdigest()==source['sha256']
        loaded[name]=json.loads(raw)
    original=loaded['objects.json']
    ids=[x['id'] for x in d['definitions']]
    assert len(ids)==len(set(ids)) and set(ids)==set(original['definitions'])
    families={x['id'] for x in json.loads((MAP/'prior_art/families.json').read_text())['families']}
    for node in d['definitions']:
        assert node['pointer']=='/definitions/'+node['id']
        assert node['effects']==original['definitions'][node['id']]['effects']
        assert node['families'] and set(node['families'])<=families
        if node['id']=='fetch.capture':
            assert node['contract_coverage']=='capture_schema' and node['schema_pointer']=='/$defs/capture'
            assert loaded['capture.schema.json']['$defs']['capture']['properties']['format']['const']=='basket.data_capture@1'
        else:
            assert node['contract_coverage']=='descriptive_not_complete' and node['schema_pointer'] is None
    for key in ('flow','instances','compositions'):assert d[key]==original[key]
    assert d['evidence']['source']=='probe-evidence.json' and d['evidence']['production_qualified'] is False
    assert loaded['probe-evidence.json']['source_capture']['historical_first_available_at'] is None
    assert d['availability_bridge']['compatible'] is False
    assert d['availability_bridge']['owner_issue']==103 and len(d['availability_bridge']['acceptance'])>=3
    assert d['remaining_gaps']

def main():
    d=json.loads((HERE/'projection.json').read_text());validate(d)
    changes={}
    def bad(name):
        v=copy.deepcopy(d);changes[name]=v;return v
    bad('source_digest_drift')['sources']['objects.json']['sha256']='0'*64
    bad('missing_definition')['definitions'].pop()
    bad('wrong_instance_binding')['instances'][0]['definition']='consumer.summary'
    bad('changed_effects')['definitions'][0]['effects']=[]
    bad('false_contract_coverage')['definitions'][0]['contract_coverage']='capture_schema'
    bad('unsafe_availability_alias')['availability_bridge']['compatible']=True
    bad('false_production')['evidence']['production_qualified']=True
    results=[{'id':'valid_projection','result':'accepted'}]
    for name,v in changes.items():
        try:validate(v)
        except (AssertionError,KeyError):results.append({'id':name,'result':'rejected'})
        else:raise AssertionError(name)
    assert {x['id'] for x in results}=={x['id'] for x in json.loads((HERE/'cases.json').read_text())['cases']}
    print(json.dumps({'evidence_class':'executed_offline_pinned_projection_checks','results':results,'external_effects':0,'source_implementation_executed':False,'production_qualified':False},indent=2))
if __name__=='__main__':main()
