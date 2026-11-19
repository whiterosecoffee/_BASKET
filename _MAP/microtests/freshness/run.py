"""Offline AM1 experiment; no network, source writes, or production invocation."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import jsonschema
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def load(p):
    return json.loads(p.read_text())
def stamp(value):
    result = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timezone required')
    return result

def main():
    contract = load(HERE / 'contract.json')
    archived = {}
    for ref in contract['source_archives']:
        raw = subprocess.check_output(['git', 'show', ref['commit'] + ':' + ref['path']], cwd=ROOT)
        assert hashlib.sha256(raw).hexdigest() == ref['sha256']
        archived[ref['path']] = raw
    old_schema = json.loads(archived['schemas/freshness.v1.json'])
    # Inspected module contains definitions/imports only; invoke only pure state().
    old = {'__name__': 'archived_observations'}
    exec(compile(archived['runtime/observations.py'], '<pinned observations>', 'exec'), old)
    payload = load(HERE / 'payload.schema.json')
    for shape in payload['$defs'].values():
        jsonschema.Draft202012Validator.check_schema(shape)
    checker = jsonschema.FormatChecker()
    def model(request):
        jsonschema.validate(request, payload['$defs']['request'], format_checker=checker)
        obs = request['observation']
        jsonschema.validate(obs, old_schema, format_checker=checker)
        now = stamp(request['as_of'])
        observed, available, ingested = [stamp(obs[k]) for k in ('observed_at', 'available_at', 'ingested_at')]
        if available > now or ingested > now:
            state = 'unavailable'
        elif observed > now:
            state = 'conflicted'
        elif obs['value'] is None:
            state = 'unavailable'
        else:
            state = 'fresh' if now < observed + dt.timedelta(seconds=obs['ttd_seconds']) else 'stale'
        return {'state': state, 'eligible_current': state == 'fresh', 'historical_source_preserved': True}
    cases = load(HERE / 'cases.json')['cases']
    results = []
    for case in cases:
        request = copy.deepcopy(case['input']); before = json.dumps(request, sort_keys=True)
        jsonschema.validate(request['observation'], old_schema, format_checker=checker)
        baseline = old['state'](request['observation'], request['as_of'])
        result = model(request)
        jsonschema.validate(result, payload['$defs']['result'])
        assert result == case['expected'], case['id']
        assert baseline == result['state'], case['id']
        assert json.dumps(request, sort_keys=True) == before
        results.append({'id': case['id'], 'archived_schema': 'accepts_shape', 'archived_runtime_state': baseline, 'test_model_result': result, 'difference_class': case['difference_class']})
    negatives = []
    for kind in ('missing_source', 'negative_ttd', 'naive_as_of', 'bad_observed'):
        request = copy.deepcopy(cases[0]['input'])
        if kind == 'missing_source': del request['observation']['source']
        elif kind == 'negative_ttd': request['observation']['ttd_seconds'] = -1
        elif kind == 'naive_as_of': request['as_of'] = '2026-01-01T00:00:30'
        else: request['observation']['observed_at'] = 'not-a-time'
        try: model(request)
        except (ValueError, jsonschema.ValidationError): negatives.append(kind)
        else: raise AssertionError('invalid input accepted: ' + kind)
    try: jsonschema.validate({'state':'fresh'}, payload['$defs']['result'])
    except jsonschema.ValidationError: pass
    else: raise AssertionError('invalid output accepted')
    for state, eligible in [('stale', True), ('fresh', False)]:
        try:
            jsonschema.validate({'state':state, 'eligible_current':eligible, 'historical_source_preserved':True}, payload['$defs']['result'])
        except jsonschema.ValidationError: pass
        else: raise AssertionError('contradictory output accepted')
    print(json.dumps({'contradictory_outputs_rejected':2, 'evidence_class':'executed_offline_microtest','results':results,'negative_inputs_rejected':negatives,'invalid_output_rejected':True,'archive_hashes_verified':True,'source_mutation':False,'not_claimed':['production component','general nested workflow execution','provider qualification','queue write']}, indent=2))
if __name__ == '__main__': main()
