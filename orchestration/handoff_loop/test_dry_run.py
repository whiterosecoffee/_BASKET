"""Disposable harness tests: subprocesses exercise restart/crash, never dispatch."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import patch

from .core import digest
from .dry_run import deliver_readonly, deliver_supplied, initialize, validate_checkpoint
from .test_github_readonly import HEAD, NOW, alter, fixture


class DryRunTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)/'disposable.json'
        self.state = initialize(self.path,harness_id='disposable-test',head=HEAD)
        self.wake = dict(id='hour-1',head=HEAD,scheduled_for=NOW)
        self.responses = fixture()

    def deliver(self, wake=None, responses=None, expected=None, now=NOW):
        return deliver_supplied(self.path,wake if wake is not None else self.wake,
                                responses if responses is not None else self.responses,
                                expected_digest=expected or digest(self.state),now=now)

    def test_normal_repeat_and_next_wake(self):
        first=self.deliver()
        self.assertEqual(first['effective_decisions'],1)
        self.assertEqual(first['receipt']['decision'],'dry-run-review-next-step')
        self.assertFalse(first['dispatch_authorized'])
        before=self.path.read_bytes()
        repeated=self.deliver(responses={},now=NOW+99999)
        self.assertEqual(repeated['effective_decisions'],0)
        self.assertEqual(repeated['receipt'],first['receipt'])
        self.assertEqual(self.path.read_bytes(),before)
        current=json.loads(self.path.read_text())
        second=self.deliver(wake=dict(self.wake,id='hour-2'),expected=digest(current))
        self.assertEqual(second['receipt']['decision'],'dry-run-no-source-change')
        self.assertEqual(second['effective_decisions'],1)
        self.assertEqual(len(json.loads(self.path.read_text())['receipts']),2)

    def test_restart_replays_without_read_or_second_receipt(self):
        first=self.deliver()
        before=self.path.read_bytes()
        script='''import json,sys
from unittest.mock import patch
from orchestration.handoff_loop.dry_run import deliver_readonly
data=json.loads(sys.stdin.read())
with patch('orchestration.handoff_loop.github_readonly._read_responses',side_effect=AssertionError('must not read')):
 result=deliver_readonly(data['path'],data['wake'],expected_digest='old-digest')
print(json.dumps(result))
'''
        process=subprocess.run([sys.executable,'-c',script],input=json.dumps({'path':str(self.path),'wake':self.wake}),capture_output=True,text=True,check=True)
        result=json.loads(process.stdout)
        self.assertEqual(result['effective_decisions'],0)
        self.assertEqual(result['receipt']['receipt_id'],first['receipt']['receipt_id'])
        self.assertEqual(self.path.read_bytes(),before)

    def test_interrupted_replace_preserves_prior_bytes(self):
        before=self.path.read_bytes()
        with patch('orchestration.handoff_loop.dry_run.os.replace',side_effect=OSError('interrupted')):
            with self.assertRaises(OSError): self.deliver()
        self.assertEqual(self.path.read_bytes(),before)
        self.assertFalse(self.path.with_suffix('.json.lock').exists())
        self.assertEqual(self.deliver()['effective_decisions'],1)

    def test_lost_ack_after_commit_recovers_by_replay(self):
        from . import dry_run
        original=dry_run._atomic_write
        def lost_ack(path,state):
            original(path,state)
            raise OSError('ack lost after commit')
        with patch.object(dry_run,'_atomic_write',side_effect=lost_ack):
            with self.assertRaises(OSError): self.deliver()
        before=self.path.read_bytes()
        replay=self.deliver(responses={})
        self.assertEqual(replay['effective_decisions'],0)
        self.assertEqual(self.path.read_bytes(),before)

    def test_process_crash_before_replace_leaves_fail_closed_lock(self):
        before=self.path.read_bytes()
        script='''import json,sys,os
from unittest.mock import patch
from orchestration.handoff_loop.dry_run import deliver_supplied
data=json.loads(sys.stdin.read())
with patch('orchestration.handoff_loop.dry_run.os.replace',side_effect=lambda *args:os._exit(9)):
 deliver_supplied(data['path'],data['wake'],data['responses'],expected_digest=data['expected'],now=data['now'])
'''
        process=subprocess.run([sys.executable,'-c',script],input=json.dumps(dict(path=str(self.path),wake=self.wake,responses=self.responses,expected=digest(self.state),now=NOW)),capture_output=True,text=True)
        self.assertEqual(process.returncode,9)
        self.assertEqual(self.path.read_bytes(),before)
        with self.assertRaises(FileExistsError): self.deliver()
        self.assertEqual(self.path.read_bytes(),before)

    def test_concurrent_writer_and_cas_conflict_reject(self):
        before=self.path.read_bytes()
        lock=self.path.with_suffix('.json.lock');lock.touch()
        with self.assertRaises(FileExistsError): self.deliver()
        self.assertEqual(self.path.read_bytes(),before)
        lock.unlink()  # Test owns this sentinel; no production lock reclamation.
        with self.assertRaisesRegex(ValueError,'CAS conflict'): self.deliver(expected='wrong')
        self.assertEqual(self.path.read_bytes(),before)

    def test_invalid_wakes_do_not_read_or_write(self):
        before=self.path.read_bytes()
        for change in ({'id':''},{'id':'x'*65},{'id':True},{'head':'b'*40},{'scheduled_for':True},{'scheduled_for':NOW+1},{'scheduled_for':NOW-301},{'extra':1}):
            with self.subTest(change=change),self.assertRaises(ValueError): self.deliver(wake=dict(self.wake,**change))
            self.assertEqual(self.path.read_bytes(),before)
        first=self.deliver()
        with self.assertRaisesRegex(ValueError,'reused'): self.deliver(wake=dict(self.wake,scheduled_for=NOW-1))
        self.assertEqual(len(json.loads(self.path.read_text())['receipts']),1)

    def test_stale_inconsistent_source_preserves_bytes(self):
        before=self.path.read_bytes()
        for attack in ('stale','head','origin','digest'):
            responses=deepcopy(self.responses)
            if attack=='stale': responses['pr']['observed_at']=NOW-301
            if attack=='head': alter(responses,'pr',lambda p:p['head'].update(sha='b'*40))
            if attack=='origin': responses['pr']['source_url']='https://example.invalid'
            if attack=='digest': responses['pr']['raw_sha256']='0'*64
            with self.subTest(attack=attack),self.assertRaises(ValueError): self.deliver(responses=responses)
            self.assertEqual(self.path.read_bytes(),before)

    def test_real_read_port_unavailable_and_zero_dispatch(self):
        before=self.path.read_bytes()
        with patch('orchestration.handoff_loop.github_readonly._read_responses',return_value=(None,{'reason':'unavailable'})),patch('time.time',return_value=NOW):
            with self.assertRaisesRegex(ValueError,'source unavailable'): deliver_readonly(self.path,self.wake,expected_digest=digest(self.state))
        self.assertEqual(self.path.read_bytes(),before)
        with patch('orchestration.handoff_loop.github_readonly._read_responses',return_value=(self.responses,None)),patch('time.time',return_value=NOW),patch('subprocess.run',side_effect=AssertionError('no process/dispatch call')):
            result=deliver_readonly(self.path,self.wake,expected_digest=digest(self.state))
        self.assertEqual(result['receipt']['source_mode'],'actual-readonly-gh')
        self.assertFalse(result['receipt']['actual_scheduled_execution'])
        self.assertFalse(result['receipt']['dispatch_authorized'])

    def test_unknown_ci_and_failed_ci_are_not_success(self):
        for kind, expected in [('unknown','dry-run-request-evidence'),('failed','dry-run-review-failure')]:
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'state.json'
                state=initialize(path,harness_id='policy-test',head=HEAD)
                responses=deepcopy(self.responses)
                if kind=='unknown': alter(responses,'ci',lambda p:p.update(total_count=0,workflow_runs=[]))
                else: alter(responses,'ci',lambda p:p['workflow_runs'][0].update(conclusion='failure'))
                result=deliver_supplied(path,self.wake,responses,expected_digest=digest(state),now=NOW)
                self.assertEqual(result['receipt']['decision'],expected)

    def test_receipt_corruption_or_policy_change_rejects(self):
        self.deliver()
        state=json.loads(self.path.read_text())
        state['receipts'][0]['dispatch_authorized']=True
        with self.assertRaises(ValueError): validate_checkpoint(state)
        state=json.loads(self.path.read_text());state['implementation']['dry_run.py']='0'*64
        with self.assertRaises(ValueError): validate_checkpoint(state)

    def test_initialize_never_overwrites_existing_checkpoint(self):
        before=self.path.read_bytes()
        with self.assertRaisesRegex(ValueError,'already exists'): initialize(self.path,harness_id='other',head=HEAD)
        self.assertEqual(self.path.read_bytes(),before)

    def test_two_writers_cannot_commit_concurrently(self):
        entered, release = threading.Event(), threading.Event()
        def read(head):
            entered.set()
            if not release.wait(5): raise RuntimeError('test timeout')
            return self.responses,None
        with patch('orchestration.handoff_loop.github_readonly._read_responses',side_effect=read),patch('time.time',return_value=NOW),ThreadPoolExecutor(max_workers=1) as pool:
            first=pool.submit(deliver_readonly,self.path,self.wake,expected_digest=digest(self.state))
            try:
                self.assertTrue(entered.wait(5))
                with self.assertRaises(FileExistsError): self.deliver()
            finally:
                release.set()
            self.assertEqual(first.result(timeout=5)['effective_decisions'],1)
        self.assertEqual(len(json.loads(self.path.read_text())['receipts']),1)

    def test_composed_read_port_uses_only_two_gets(self):
        results=[subprocess.CompletedProcess([],0,stdout=self.responses[name]['raw_json'].encode(),stderr=b'') for name in ('pr','ci')]
        with patch('shutil.which',return_value='gh'),patch('subprocess.run',side_effect=results) as run,patch('time.time',return_value=NOW):
            result=deliver_readonly(self.path,self.wake,expected_digest=digest(self.state))
        self.assertEqual(run.call_count,2)
        for call in run.call_args_list:
            command=call.args[0]
            self.assertEqual(command[:2],['gh','api'])
            self.assertEqual(command[command.index('--method')+1],'GET')
            self.assertEqual(command[command.index('--hostname')+1],'github.com')
        self.assertFalse(result['dispatch_authorized'])
