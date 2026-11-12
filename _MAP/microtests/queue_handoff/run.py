"""Pinned archived pure guard calls and bounded in-memory handoff test model."""
import copy
import datetime as dt
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def load(path): return json.loads(path.read_text())
def experiment(bridge, manager, fixtures, case):
    task = fixtures['task_id']; aid = fixtures['attempt_id']; head = fixtures['head_sha']
    now = dt.datetime.fromisoformat(fixtures['as_of'].replace('Z', '+00:00'))
    def event(eid, kind, **kw):
        return dict(schema='basket.agentic_event@1', event_id=eid, type=kind, task_id=task, at='2026-01-01T00:00:00Z', **kw)
    lease = event('lease-1', 'lease_granted', issue=230, branch='work/230-map-system-planning', expires_at='2026-01-01T00:10:00Z')
    start = event('start-1', 'attempt_started', attempt_id=aid, step_id='S1')
    result = event('result-1', 'attempt_passed', attempt_id=aid, step_id='S1', result_url='https://example.invalid/synthetic/result')
    acceptance = event('review-1','acceptance_verified',criterion_id='A1', source_url='https://example.invalid/synthetic/review',independent_reviewer='synthetic-reviewer',head_sha=head)
    events = [lease, start]; trace=[]; variant=case['id']; result_count=0
    def output(outcome):
        return {'id':variant,'outcome':outcome,'next_proposal':outcome=='next_proposal','external_effects':0,'result_count':result_count,'trace':trace}
    if variant=='expired_claim': lease['expires_at']='2026-01-01T00:00:30Z'
    fence='old-lease' if variant=='stale_claim' else 'lease-1'
    try:
        bridge.assert_fence(manager,events,task,fence,now)
        bridge.assert_attempt(manager,events,task,aid)
    except bridge.Blocked as exc:
        trace.append({'stage':'claim','result':exc.code});return output(exc.code)
    trace.append({'stage':'claim','result':'valid'})
    if variant.startswith('uncertain_'):
        readback=case['readback']
        expected={'target_scope':'synthetic-queue-only','task_id':task,'attempt_id':aid,'step_id':'S1','head_sha':head,'event_id':result['event_id'],'kind':result['type'],'payload':{'result_url':result['result_url']}}
        def digest(value):
            return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        observed=readback['result']
        matches=(isinstance(observed,dict) and observed.get('envelope')==expected and observed.get('sha256')==digest(observed['envelope'])==digest(expected))
        observation=('unknown' if readback['status']!='observed' else 'absent' if observed is None else 'matching' if matches else 'mismatch')
        trace.append({'stage':'readback','result':observation,'implementation':'new_offline_model'})
        if observation!='matching':
            return output({'absent':'retry_requires_fresh_authority_and_state','unknown':'inspect_before_retry','mismatch':'write_conflict'}[observation])
        # Same fixture identity already exists; consume without another append/effect.
        envelope=observed['envelope']
        consumed=event(envelope['event_id'],envelope['kind'],attempt_id=envelope['attempt_id'],step_id=envelope['step_id'],result_url=envelope['payload']['result_url'])
        assert consumed['task_id']==envelope['task_id']
        events.append(consumed);result_count=1
        assert events[-1]['attempt_id']==aid and events[-1]['event_id']==result['event_id']
    else:
        events.append(result);result_count=1
    manager.event_check(events,now);manager.attempts(events,task)
    if variant=='duplicate_result':
        replay=copy.deepcopy(result);replay['event_id']='result-duplicate'
        try: manager.attempts(events+[replay],task)
        except manager.GuardError:
            trace.append({'stage':'result','result':'duplicate_rejected'});return output('duplicate_result_rejected')
        raise AssertionError('duplicate result accepted')
    trace.append({'stage':'result','result':'one_observed_result'})
    if variant=='wrong_head_acceptance': acceptance['head_sha']='b'*40
    if variant!='missing_acceptance':events.append(acceptance)
    manager.event_check(events,now)
    ci={'head_sha':head,'name':'Validate BASKET data','conclusion':'failure' if variant=='failed_ci' else 'success'}
    verdict=manager.acceptance({'id':task,'acceptance':['A1']},{'head_sha':head,'merged':False},{'workflow_runs':[ci],'main_commit':'c'*40},events)
    trace.append({'stage':'acceptance','result':verdict})
    if not verdict['component_verified']:return output('acceptance_blocked')
    assert verdict['integrated'] is False
    trace.append({'stage':'next','result':'eligible_proposal_only'})
    return output('next_proposal')
def main():
    contract=load(HERE/'contract.json');fixtures=load(HERE/'cases.json');results=[]
    # Read-only pinned repository materialized only into ephemeral scratch.
    with tempfile.TemporaryDirectory(prefix='map-queue-archive-') as tmp:
        target=Path(tmp);archive=target/'source.tar'
        subprocess.check_call(['git','archive','--format=tar','--output',str(archive),contract['archive_commit']],cwd=ROOT)
        with tarfile.open(archive) as tar:tar.extractall(target/'source',filter='data')
        source=target/'source'
        for ref in contract['archive_sources']:
            assert hashlib.sha256((source/ref['path']).read_bytes()).hexdigest()==ref['sha256']
        sys.path.insert(0,str(source))
        bridge=importlib.import_module('orchestration.worker_bridge.bridge')
        manager=importlib.import_module('orchestration.agentic.manager')
        for case in fixtures['cases']:
            before=json.dumps(fixtures,sort_keys=True)
            result=experiment(bridge,manager,fixtures,case)
            assert result['outcome']==case['expected_outcome'],case['id']
            assert result['next_proposal']==case['expected_next']
            assert result['external_effects']==case['expected_external_effects']==0
            assert json.dumps(fixtures,sort_keys=True)==before
            results.append(result)
    print(json.dumps({'evidence_class':'executed_offline_microtest','archive_commit':contract['archive_commit'],'cases':results,'archive_hashes_verified':True,'external_effects':0,'not_claimed':['live queue execution','autonomous orchestration','real independent acceptance','production uncertain-write adapter']},indent=2))
if __name__=='__main__':main()
