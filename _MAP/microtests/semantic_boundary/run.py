"""AM2 offline semantic-boundary experiment; no effects or implicit conversion."""
import hashlib
import json
from pathlib import Path
import subprocess
import jsonschema
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def load(p):return json.loads(p.read_text())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def match(q,shape,archive):
    jsonschema.validate(q,shape)
    if digest(q['payload'])!=q['payload_sha256']:return 'payload_hash_mismatch'
    jsonschema.validate(q['payload'],archive,format_checker=jsonschema.FormatChecker())
    s,c=q['semantics'],q['consumer']
    if c['schema_major']!=1:return 'schema_version_unsupported'
    if q['schema_version']!='1.0.0':return 'schema_version_mismatch'
    for field in ('unit','session','rights','time_basis','freshness'):
        if not s[field]:return field+'_unknown'
        if (s[field] not in c[field] if field=='rights' else s[field]!=c[field]):return field+'_mismatch'
    value=q['payload']['value']
    if value['adjustment_basis']!=c['adjustment_basis']:return 'basis_mismatch'
    if value['interval']!=c['interval']:return 'interval_mismatch'
    if c['volume'] not in ('integer_only','fractional_allowed'):return 'volume_policy_unknown'
    if c['volume']=='integer_only' and value['volume']%1!=0:return 'fractional_volume_mismatch'
    return 'compatible'
def main():
    contract=load(HERE/'contract.json');ref=contract['archive']
    raw=subprocess.check_output(['git','show',ref['commit']+':'+ref['path']],cwd=ROOT)
    assert hashlib.sha256(raw).hexdigest()==ref['sha256'];archive=json.loads(raw)
    shape=load(HERE/'request.schema.json');jsonschema.Draft202012Validator.check_schema(shape)
    cases=load(HERE/'cases.json')['cases'];results=[]
    for case in cases:
        q=case['request'];before=digest(q)
        # Observe archive behavior independently: all fixtures have valid domain shape.
        jsonschema.validate(q['payload'],archive,format_checker=jsonschema.FormatChecker())
        outcome=match(q,shape,archive)
        assert outcome==case['expected'],case['id'];assert before==digest(q)
        results.append({'id':case['id'],'archived_shape':'accepted','outcome':outcome,'input_unchanged':True})
    print(json.dumps({'evidence_class':'executed_offline_microtest','results':results,'external_effects':0,'archive_hash_verified':True,'not_claimed':['production compatibility','real entitlement','live freshness','full system completion']},indent=2))
if __name__=='__main__':main()
