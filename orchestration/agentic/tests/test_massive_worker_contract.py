import datetime as dt
import copy
import unittest
from orchestration.agentic import massive_worker_contract as w

NOW = '2026-10-17T21:00:00+00:00'

class MassiveWorkerContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = w.load()
        self.provider = dict(self.spec['provider_observed_capabilities'])

    def test_spec_valid(self):
        self.assertTrue(w.validate_specs(self.spec))

    def test_all_owner_paths_are_scoped(self):
        for job in self.spec['workers']:
            self.assertTrue(all(any(p.startswith(x) for x in w.OWNERS[job['owner']]) for p in job['writes']))

    def test_unknown_capabilities_cannot_invent_feed(self):
        output = w.reconcile(self.spec, self.provider, NOW)
        lookup = {x['id']: x for x in output['workers']}
        self.assertEqual(lookup['B02-live']['dispatch'], 'blocked_entitlement')
        self.assertEqual(lookup['B02-eod']['dispatch'], 'blocked_backend_credentials')
        self.assertEqual(lookup['B02-minute']['dispatch'], 'verification_required')
        self.assertFalse(any(j['running'] or j['live_usable'] for j in output['workers']))

    def test_upgrade_requires_direct_backend_credentials(self):
        self.provider.update(last_trade='available', backend_credentials='available')
        x = next(j for j in w.reconcile(self.spec, self.provider, NOW)['workers'] if j['id']=='B02-live')
        self.assertEqual(x['dispatch'], 'eligible_not_running')
        self.assertFalse(x['running'])

    def test_rejects_chat_plugin_background(self):
        clone=copy.deepcopy(self.spec)
        clone['workers'][0]['transport']='chatgpt_plugin_background'
        with self.assertRaises(ValueError): w.validate_specs(clone)

    def test_rejects_invalid_worker_cadence(self):
        clone=copy.deepcopy(self.spec)
        clone['workers'][0]['cadence_seconds']=0
        with self.assertRaises(ValueError): w.validate_specs(clone)

    def test_b01_cannot_steal_b02_unit_test(self):
        clone=copy.deepcopy(self.spec)
        job=next(j for j in clone['workers'] if j['owner']=='B01')
        job['writes']=['tests/test_ttd.py']
        with self.assertRaises(ValueError): w.validate_specs(clone)

    def test_rejects_cross_domain_write(self):
        clone=copy.deepcopy(self.spec)
        clone['workers'][0]['writes']=['deployment/secrets.env']
        with self.assertRaises(ValueError): w.validate_specs(clone)

    def test_duplicate_jobs_rejected(self):
        clone=copy.deepcopy(self.spec)
        clone['workers'].append(copy.deepcopy(clone['workers'][0]))
        with self.assertRaises(ValueError): w.validate_specs(clone)

    def sample(self,age=30):
        time=dt.datetime.fromisoformat(NOW)
        return {'source':'Massive', 'ticker':'NVDA', 'event_at':(time-dt.timedelta(seconds=age)).isoformat(),
                'available_at':(time-dt.timedelta(seconds=age-1)).isoformat(),
                'ingested_at':(time-dt.timedelta(seconds=age-2)).isoformat(),
                'observed_at':NOW, 'currency':'USD'}

    def test_live_requires_runtime_and_fresh_heartbeat(self):
        self.provider.update(last_trade='available', backend_credentials='available')
        obs={'B02-live':self.sample()}
        def result(verified, when):
            return next(j for j in w.reconcile(self.spec,self.provider,NOW,obs,verified,{'B02-live':when})['workers'] if j['id']=='B02-live')
        self.assertFalse(result(False,NOW)['live_usable'])
        self.assertTrue(result(True,NOW)['live_usable'])
        self.assertFalse(result(True,'2026-10-17T20:50:00+00:00')['running'])

    def test_quote_freshness(self):
        self.assertEqual(w.freshness(self.sample(30),NOW,60),'fresh_as_of')
        self.assertEqual(w.freshness(self.sample(150),NOW,60),'expired_historical')

    def test_time_order_violation(self):
        obs=self.sample()
        obs['available_at']=NOW
        self.assertEqual(w.freshness(obs,NOW,60),'invalid_time_order')

    def test_naive_date_rejected(self):
        obs=self.sample()
        obs['event_at']='2026-10-17T20:59:30'
        self.assertEqual(w.freshness(obs,NOW,60),'invalid_timestamp')

    def test_empty_provenance_rejected(self):
        obs=self.sample()
        del obs['source']
        self.assertEqual(w.freshness(obs,NOW,60),'missing_provenance')

    def test_fresh_data_cannot_override_entitlement(self):
        observations={'B02-live':self.sample()}
        jobs=w.reconcile(self.spec,self.provider,NOW,observations)['workers']
        live=next(i for i in jobs if i['id']=='B02-live')
        self.assertEqual(live['observation'],'fresh_as_of')
        self.assertFalse(live['live_usable'])

if __name__=='__main__': unittest.main()