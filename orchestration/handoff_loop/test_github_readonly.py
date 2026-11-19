"""Forged fixtures test validation only; real read evidence is stored separately."""
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import subprocess
import unittest
from unittest.mock import patch

from .github_readonly import API, WEB, BRANCH, REPOSITORY, collect, endpoints, normalize_supplied

HEAD = 'a' * 40
NOW = datetime.fromisoformat('2026-11-13T00:00:00+00:00').timestamp()


def fixture():
    paths = endpoints(HEAD)
    pr = dict(number=264,id=42,url=API+paths['pr'],html_url=f'{WEB}/{REPOSITORY}/pull/264',
              head={'sha':HEAD,'ref':BRANCH,'repo':{'full_name':REPOSITORY}},
              base={'ref':'main','repo':{'full_name':REPOSITORY}},state='open',draft=True,
              created_at='2026-11-12T00:00:00Z',updated_at='2026-11-12T23:00:00Z')
    run = dict(id=123,url=f'{API}/repos/{REPOSITORY}/actions/runs/123',html_url=f'{WEB}/{REPOSITORY}/actions/runs/123',
               head_sha=HEAD,repository={'full_name':REPOSITORY},status='completed',conclusion='success',
               name='Shared validation',created_at='2026-11-12T23:00:00Z',updated_at='2026-11-12T23:01:00Z')
    bodies = {'pr':pr,'ci':{'total_count':1,'workflow_runs':[run]}}
    return {name:dict(source_url=API+paths[name],observed_at=NOW,raw_json=json.dumps(body),
                       raw_sha256=hashlib.sha256(json.dumps(body).encode()).hexdigest()) for name,body in bodies.items()}


def alter(responses, name, change):
    body = json.loads(responses[name]['raw_json'])
    change(body)
    responses[name]['raw_json'] = json.dumps(body)
    responses[name]['raw_sha256'] = hashlib.sha256(responses[name]['raw_json'].encode()).hexdigest()


class GitHubReadonlyTests(unittest.TestCase):
    def test_deterministic_supplied_normalization_is_not_verified_retrieval(self):
        responses = fixture()
        before = deepcopy(responses)
        result = normalize_supplied(responses,head=HEAD,now=NOW)
        self.assertEqual(result,normalize_supplied(responses,head=HEAD,now=NOW))
        self.assertEqual(result['ci']['runs'][0]['conclusion'],'success')
        self.assertFalse(result['retrieval']['verified_local_retrieval'])
        self.assertFalse(result['component_tests_verified'])
        self.assertFalse(result['reviewer_acceptance'])
        self.assertFalse(result['execution_authorized'])
        self.assertIsNone(result['evaluator_observation'])
        self.assertEqual(responses,before)

    def test_substituted_origins_and_forged_transport_label(self):
        for name in ('pr','ci'):
            for origin in ('http://api.github.com','https://example.invalid','https://api.github.com.evil.invalid'):
                responses = fixture()
                responses[name]['source_url'] = responses[name]['source_url'].replace(API,origin)
                with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)
        responses = fixture()
        responses['pr']['verified_local_retrieval'] = True
        with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)
        for name, change in (
            ('pr',lambda p:p.update(url='https://example.invalid/pulls/264')),
            ('ci',lambda p:p['workflow_runs'][0].update(html_url='https://example.invalid/run/123'))):
            responses=fixture();alter(responses,name,change)
            with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)

    def test_wrong_subject_and_changed_revision(self):
        changes = [lambda p:p.update(number=265),lambda p:p['head']['repo'].update(full_name='other/repo'),
                   lambda p:p['base']['repo'].update(full_name='other/repo'),lambda p:p['head'].update(sha='b'*40),
                   lambda p:p['head'].update(ref='work/other')]
        for change in changes:
            responses=fixture();alter(responses,'pr',change)
            with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)
        for change in (lambda p:p['workflow_runs'][0].update(head_sha='b'*40),lambda p:p['workflow_runs'][0]['repository'].update(full_name='other/repo')):
            responses=fixture();alter(responses,'ci',change)
            with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)

    def test_invalid_stale_future_times(self):
        for stamp in (NOW-301,NOW+1,None,True,'today',float('nan')):
            responses=fixture();responses['pr']['observed_at']=stamp
            with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)
        for stamp in ('2026-11-13T00:00:01Z','2026-11-12T00:00:00','yesterday',None,'2026-15-99T00:00:00Z'):
            for name in ('pr','ci'):
                responses=fixture()
                alter(responses,name,lambda b:(b if name=='pr' else b['workflow_runs'][0]).update(updated_at=stamp))
                with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)

    def test_missing_fields_and_digest_tampering(self):
        for name in ('pr','ci'):
            responses=fixture();responses[name]['raw_json']+=' '
            with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)
        for field in ('head','number','updated_at','draft'):
            responses=fixture();alter(responses,'pr',lambda p:p.pop(field))
            with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)
        responses=fixture();alter(responses,'ci',lambda p:p.pop('workflow_runs'))
        with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)

    def test_duplicate_run_and_replayed_observation(self):
        responses=fixture()
        result=normalize_supplied(responses,head=HEAD,now=NOW)
        # A later fetch of identical source content is still the same observation.
        for row in responses.values(): row['observed_at']+=1
        replay=normalize_supplied(responses,head=HEAD,now=NOW+1,seen_observations=[result['observation_id']])
        self.assertEqual(replay['disposition'],'no-change')
        self.assertEqual(replay['acceptance_receipts'],[])
        self.assertFalse(replay['execution_authorized'])
        with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW+1,seen_observations=['same','same'])
        alter(responses,'ci',lambda p:(p['workflow_runs'].append(deepcopy(p['workflow_runs'][0])),p.update(total_count=2)))
        with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW+1)

    def test_unknown_ci_is_not_failure_or_success(self):
        for ci in ({'total_count':0,'workflow_runs':[]},{'total_count':2,'workflow_runs':json.loads(fixture()['ci']['raw_json'])['workflow_runs']}):
            responses=fixture();alter(responses,'ci',lambda p:(p.clear(),p.update(ci)))
            result=normalize_supplied(responses,head=HEAD,now=NOW)
            self.assertEqual(result['ci']['availability'],'unknown')
            self.assertFalse(result['component_tests_verified'])

    def test_rejection_nonmutation(self):
        responses=fixture();alter(responses,'pr',lambda p:p['head'].update(sha='b'*40))
        before=deepcopy(responses)
        with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)
        self.assertEqual(responses,before)

    def test_collector_only_issues_allowlisted_gets(self):
        responses=fixture()
        calls=[subprocess.CompletedProcess([],0,stdout=responses[name]['raw_json'].encode(),stderr=b'') for name in ('pr','ci')]
        with patch('shutil.which',return_value='gh'),patch('subprocess.run',side_effect=calls) as run,patch('time.time',return_value=NOW):
            result=collect(head=HEAD)
        self.assertTrue(result['retrieval']['verified_local_retrieval'])
        self.assertFalse(result['source_claims_verified'])
        for call,path in zip(run.call_args_list,endpoints(HEAD).values()):
            args=call.args[0]
            self.assertEqual(args[args.index('--method')+1],'GET')
            self.assertEqual(args[args.index('--hostname')+1],'github.com')
            self.assertEqual(args[-1],path)
        self.assertEqual(run.call_count,2)

    def test_unavailable_sanitizes_failures_and_never_retries(self):
        with patch('shutil.which',return_value=None):
            self.assertEqual(collect(head=HEAD)['availability'],'unavailable')
        with patch('shutil.which',return_value='gh'),patch('subprocess.run',return_value=subprocess.CompletedProcess([],1,stdout=b'',stderr=b'private diagnostic')) as run:
            result=collect(head=HEAD)
        self.assertEqual(run.call_count,1)
        self.assertEqual(result['availability'],'unavailable')
        self.assertNotIn('private diagnostic',json.dumps(result))

    def test_duplicate_json_keys_reject(self):
        responses=fixture()
        responses['ci']['raw_json']='{"total_count":0,"total_count":1,"workflow_runs":[]}'
        responses['ci']['raw_sha256']=hashlib.sha256(responses['ci']['raw_json'].encode()).hexdigest()
        with self.assertRaises(ValueError): normalize_supplied(responses,head=HEAD,now=NOW)
