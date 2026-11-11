"""Two fixed offline compositions through shared clean typed primitive definitions."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import jsonschema
HERE=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def stamp(x):
    value=dt.datetime.fromisoformat(x.replace('Z','+00:00'))
    if value.tzinfo is None:raise ValueError('timezone required')
    return value

def evaluate(case,model,schemas):
    trace=[];config=model['use_cases'][case['use_case']]
    def validate(value,ref):
        assert ref.startswith('schemas.json#/$defs/')
        jsonschema.validate(value,schemas['$defs'][ref.rsplit('/',1)[1]],format_checker=jsonschema.FormatChecker())
    def call(name,value,fn):
        contract=model['definitions'][name];validate(value,contract['input'])
        result=fn(copy.deepcopy(value));validate(result,contract['output'])
        trace.append({'definition':name,'input_hash':digest(value),'output_hash':digest(result),'boundary':'validated'})
        return result
    def semantics(q):
        errors=[]
        for key,expected in config['required_semantics'].items():
            actual=q['semantics'].get(key)
            if actual is None:errors.append(key+'_missing')
            elif actual!=expected:errors.append(key+'_mismatch')
        if stamp(q['available_at'])>stamp(q['as_of']):errors.append('not_available_at_cutoff')
        age=(stamp(q['as_of'])-stamp(q['observed_at'])).total_seconds()
        if age<0:errors.append('future_observation')
        elif config['max_age_seconds'] is not None and age>=config['max_age_seconds']:errors.append('expired')
        return {'request':q,'violations':errors}
    def report(q):
        errors=q['violations'];return {'source_id':q['request']['source_id'],'status':'rejected' if errors else 'accepted','value':None if errors else q['request']['value'],'reasons':errors}
    def outer(q):
        qualified=call('qualify',q,lambda child:call('check_semantics',child,semantics))
        return call('render_report',qualified,report)
    before=digest(case['input'])
    try:result=call('admit',case['input'],outer)
    except (jsonschema.ValidationError,ValueError):
        assert case['expected_reason']=='invalid_input'
        result={'error':'invalid_input'}
    else:
        reason=case['expected_reason']
        assert result['reasons']==([] if reason is None else [reason])
        assert result['status']==('accepted' if reason is None else 'rejected')
    assert digest(case['input'])==before
    return {'id':case['id'],'use_case':case['use_case'],'result':result,'trace':trace,'input_unchanged':True}

def validate_graph(model):
    instances={x['id']:x for x in model['instances']};assert len(instances)==len(model['instances'])
    for node in instances.values():
        assert node['definition'] in model['definitions']
        seen={node['id']};parent=node['parent']
        while parent is not None:
            assert parent in instances and parent not in seen
            seen.add(parent);parent=instances[parent]['parent']
    for edge in model['delegation']:
        refs=[]
        for endpoint in (edge['from'],edge['to']):
            instance,port=endpoint.split('.');assert port in ('input','output')
            refs.append(model['definitions'][instances[instance]['definition']][port])
        assert refs[0]==refs[1],edge
    # Harness is intentionally fixed; refuse a graph it does not execute.
    assert {(n['id'], n['definition'], n['parent']) for n in model['instances']} == {('outer','admit',None),('qualification','qualify','outer'),('semantic_check','check_semantics','qualification'),('report','render_report','outer')}
    assert model['delegation']==[{'from':a,'to':b} for a,b in [('outer.input','qualification.input'),('qualification.input','semantic_check.input'),('semantic_check.output','qualification.output'),('qualification.output','report.input'),('report.output','outer.output')]]
def main():
    model=load(HERE/'composition.json');schemas=load(HERE/'schemas.json');cases=load(HERE/'cases.json')['cases']
    validate_graph(model)
    for schema in schemas['$defs'].values():jsonschema.Draft202012Validator.check_schema(schema)
    ids={c['id'] for c in cases};assert len(ids)==len(cases)
    for req in model['requirements']:
        assert req['cases'] and set(req['cases'])<=ids
        assert req['definitions'] and set(req['definitions'])<=set(model['definitions'])
    results=[evaluate(c,model,schemas) for c in cases]
    positive=[r for r in results if r['id'] in ('market_ok','filing_ok')]
    assert len(positive)==2
    assert all({t['definition'] for t in r['trace']}==set(model['definitions']) for r in positive)
    # Output invariant and graph mutation negatives are real checks, not expected-only prose.
    negatives=0
    try:jsonschema.validate({'source_id':'x','status':'rejected','value':1,'reasons':['bad']},schemas['$defs']['report'])
    except jsonschema.ValidationError:negatives+=1
    bad=copy.deepcopy(model);bad['instances'][0]['parent']='semantic_check'
    try:validate_graph(bad)
    except AssertionError:negatives+=1
    bad=copy.deepcopy(model);bad['definitions']['render_report']['input']='schemas.json#/$defs/request'
    try:validate_graph(bad)
    except AssertionError:negatives+=1
    assert negatives==3
    print(json.dumps({'evidence_class':'executed_offline_reference_composition','results':results,'requirements_covered':[q['id'] for q in model['requirements']],'graph_and_output_negatives':negatives,'shared_clean_primitives':['check_semantics','render_report'],'external_effects':0,'production_qualified':False},indent=2))
if __name__=='__main__':main()
