"""No authenticated trigger fixture exists: every positive is simulated."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from .core import digest
from .dry_run import initialize
from .trigger_bridge import admit_live_trigger, checkpoint_binding, deliver_simulated_trigger, simulate_binding
from .test_github_readonly import HEAD, NOW, fixture


def binding_fixture(state):
    pins=dict(provider='fixture-scheduler',automation_id='fixture-task',target_session='fixture-session',
              environment_id='fixture-environment',owner_id='fixture-owner',lease_id='fixture-lease',lease_fence=7,
              checkpoint_id=state['harness_id'],checkpoint_binding=checkpoint_binding(state),head=HEAD)
    trigger={key:pins[key] for key in ('provider','automation_id','target_session','environment_id','checkpoint_id','checkpoint_binding','head')}
    trigger.update(mode='simulated',original_run_id='run-1',delivery_id='delivery-1',scheduled_for=NOW,issued_at=NOW,observed_at=NOW)
    owner={key:pins[key] for key in ('owner_id','target_session','environment_id','head')}
    owner.update(mode='simulated',source_id='synthetic://owner',active=True,observed_at=NOW)
    lease={key:pins[key] for key in ('lease_id','owner_id','target_session','environment_id','checkpoint_id','checkpoint_binding','head')}
    lease.update(mode='simulated',source_id='synthetic://lease',exclusive=True,fence=7,observed_at=NOW,expires_at=NOW+300)
    return pins,trigger,owner,lease


class TriggerBridgeTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)/'disposable.json'
        self.state=initialize(self.path,harness_id='trigger-fixture',head=HEAD)
        self.args=binding_fixture(self.state)

    def test_live_boundary_never_opens_checkpoint_or_dispatches(self):
        before=self.path.read_bytes()
        for payload in (None,{}, {'verified':True,'run_id':'fabricated'}, {'prompt':'forwarded wake'}):
            with patch.object(Path,'read_text',side_effect=AssertionError('no read')),patch('subprocess.run',side_effect=AssertionError('no dispatch')),patch('orchestration.handoff_loop.trigger_bridge.deliver_supplied',side_effect=AssertionError('no write')):
                result=admit_live_trigger(self.path,payload)
            self.assertEqual(result['status'],'blocked')
            self.assertFalse(result['actual_trigger_verified'])
            self.assertFalse(result['checkpoint_written'])
            self.assertEqual(self.path.read_bytes(),before)

    def test_binding_deterministic_and_retry_delivery_id_ignored(self):
        before=deepcopy(self.args)
        first=simulate_binding(*self.args,now=NOW)
        self.assertEqual(first,simulate_binding(*self.args,now=NOW))
        changed=deepcopy(self.args);changed[1]['delivery_id']='delivery-2'
        self.assertEqual(first['wake'],simulate_binding(*changed,now=NOW)['wake'])
        self.assertFalse(first['actual_trigger_verified'])
        self.assertFalse(first['ownership_verified'])
        self.assertEqual(self.args,before)

    def test_missing_or_unsupported_evidence_rejects(self):
        for index,record in enumerate(self.args):
            for field in record:
                args=deepcopy(self.args);del args[index][field]
                with self.subTest(index=index,field=field),self.assertRaises(ValueError): simulate_binding(*args,now=NOW)
        for index in (1,2,3):
            args=deepcopy(self.args);args[index]['mode']='verified-real'
            with self.assertRaises(ValueError): simulate_binding(*args,now=NOW)
        args=deepcopy(self.args);args[0]['provider']='hosted-automation'
        with self.assertRaises(ValueError): simulate_binding(*args,now=NOW)

    def test_stale_inconsistent_owner_and_lease_preserve_bytes(self):
        before=self.path.read_bytes()
        changes=[(1,'observed_at',NOW-301),(1,'issued_at',NOW+1),(2,'observed_at',NOW-301),
                 (2,'active','true'),(2,'owner_id','other'),(3,'exclusive',1),(3,'expires_at',NOW),
                 (3,'fence',6),(3,'fence',True),(3,'observed_at',NOW+1),(3,'lease_id','other')]
        for index,key,value in changes:
            args=deepcopy(self.args);args[index][key]=value
            with self.subTest(index=index,key=key),self.assertRaises(ValueError):
                deliver_simulated_trigger(self.path,*args,fixture(),now=NOW,expected_digest=digest(self.state))
            self.assertEqual(self.path.read_bytes(),before)

    def test_target_and_checkpoint_binding_mismatches_reject(self):
        for index in (1,2,3):
            for key in ('target_session','environment_id','head'):
                args=deepcopy(self.args);args[index][key]='other'
                with self.assertRaises(ValueError): simulate_binding(*args,now=NOW)
        with tempfile.TemporaryDirectory() as directory:
            wrong=Path(directory)/'other.json'
            state=initialize(wrong,harness_id='other-checkpoint',head=HEAD)
            before=wrong.read_bytes()
            with self.assertRaises(ValueError): deliver_simulated_trigger(wrong,*self.args,fixture(),now=NOW,expected_digest=digest(state))
            self.assertEqual(wrong.read_bytes(),before)

    def test_original_run_identity_is_bound(self):
        first=simulate_binding(*self.args,now=NOW)
        args=deepcopy(self.args);args[1]['original_run_id']='run-2'
        self.assertNotEqual(first['wake']['id'],simulate_binding(*args,now=NOW)['wake']['id'])
        args=deepcopy(self.args);args[1]['original_run_id']=None
        with self.assertRaises(ValueError): simulate_binding(*args,now=NOW)

    def test_simulated_delivery_repeat_and_restart(self):
        first=deliver_simulated_trigger(self.path,*self.args,fixture(),now=NOW,expected_digest=digest(self.state))
        self.assertEqual(first['result']['effective_decisions'],1)
        before=self.path.read_bytes()
        args=deepcopy(self.args);args[1]['delivery_id']='retry-delivery'
        second=deliver_simulated_trigger(self.path,*args,{},now=NOW,expected_digest='old')
        self.assertEqual(second['result']['effective_decisions'],0)
        self.assertEqual(self.path.read_bytes(),before)
        script='''import json,sys
from orchestration.handoff_loop.trigger_bridge import deliver_simulated_trigger
d=json.loads(sys.stdin.read())
r=deliver_simulated_trigger(d['path'],*d['args'],{},now=d['now'],expected_digest='old')
print(json.dumps({'count':r['result']['effective_decisions'],'receipt':r['result']['receipt']['receipt_id']}))
'''
        result=subprocess.run([sys.executable,'-c',script],input=json.dumps(dict(path=str(self.path),args=args,now=NOW)),capture_output=True,text=True,check=True)
        replay=json.loads(result.stdout)
        self.assertEqual(replay['count'],0)
        self.assertEqual(replay['receipt'],first['result']['receipt']['receipt_id'])
        self.assertEqual(self.path.read_bytes(),before)

    def test_live_evidence_cannot_be_smuggled_through_simulation(self):
        args=deepcopy(self.args);args[1]['authenticated']=True
        before=self.path.read_bytes()
        with self.assertRaises(ValueError): deliver_simulated_trigger(self.path,*args,fixture(),now=NOW,expected_digest=digest(self.state))
        self.assertEqual(self.path.read_bytes(),before)
