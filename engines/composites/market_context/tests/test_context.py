import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("market_context", ROOT/"context.py")
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)


def quote(price=110, previous=100, when="2026-10-29T16:00:00Z"):
    return {"price":price,"previous_close":previous,"observed_at":when,"available_at":when,
            "source":"test_fixture","currency":"USD","session":"regular","entitlement":"realtime",
            "basis":"split_adjusted_USD","baseline_id":"2026-10-28_close","quality_flags":[],
            "vwap":105,"open":102,"high":115,"low":99}


def snapshot(when="2026-10-29T16:00:00Z"):
    return {"snapshot_id":when,"as_of":when,"available_at":when,"ingested_at":when,"session":"regular",
            "quotes":{t:quote(price,when=when) for t,price in (("A",110),("B",90),("QQQ",102),("SOXX",103))},
            "macros":[],"supersedes":None}


def registry():
    return {"registry_id":"test@1","authority":"synthetic_fixture","available_at":"2026-10-28T00:00:00Z",
            "effective_at":"2026-10-28T00:00:00Z","members":[{"ticker":"A","group":"chips","sector_proxy":"SOXX"},{"ticker":"B","group":"chips","sector_proxy":"SOXX"}],"benchmarks":["QQQ"]}


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.r=registry(); self.s=snapshot(); self.policy=json.loads((ROOT/"policy.v1.json").read_text())

    def test_daily_relative_and_open_vwap(self):
        out=c.analyze(self.r,self.s); a=out['tickers'][0]
        self.assertAlmostEqual(a['relative_qqq_pp'],8);self.assertAlmostEqual(a['relative_sector_pp'],7)
        self.assertAlmostEqual(a['above_vwap_pct'],100*(110/105-1));self.assertAlmostEqual(out['daily']['basket_mean_pct'],0)

    def test_missing_not_neutral(self):
        del self.s['quotes']['B'];out=c.analyze(self.r,self.s)
        self.assertEqual(out['daily']['coverage'],.5);self.assertIsNone(out['daily']['basket_mean_pct']);self.assertEqual(out['participation']['expected'],2)

    def test_unknown_entitlement_research_only(self):
        self.s['quotes']['A']['entitlement']='unknown'
        self.assertEqual(c.analyze(self.r,self.s)['tickers'][0]['status'],'entitlement_unknown')
        self.assertEqual(c.analyze(self.r,self.s,mode='research')['tickers'][0]['status'],'provisional')

    def test_stale_not_extended_by_capture(self):
        self.s['quotes']['A']['observed_at']='2026-10-29T15:50:00Z'
        self.assertEqual(c.analyze(self.r,self.s)['tickers'][0]['status'],'stale')

    def test_session_update_does_not_refresh_old_trade(self):
        self.s['quotes']['A']['last_trade_bar_at']='2026-10-29T15:50:00Z'
        self.assertEqual(c.analyze(self.r,self.s)['tickers'][0]['status'],'stale_trade_bar')

    def test_unresolved_symbol_not_in_aggregate(self):
        self.r['members'][0]['quote_admission']='unresolved'
        out=c.analyze(self.r,self.s)
        self.assertEqual(out['daily']['coverage'],.5);self.assertEqual(out['tickers'][0]['status'],'symbol_unverified')
        self.assertEqual(c.refresh_plan(self.r)['unresolved_symbols'],['A'])

    def test_future_quote_excluded(self):
        self.s['quotes']['A']['observed_at']='2026-10-29T16:01:00Z'
        self.assertEqual(c.analyze(self.r,self.s)['tickers'][0]['status'],'future')

    def test_duplicate_membership_rejected(self):
        self.r['members'].append(self.r['members'][0])
        with self.assertRaises(ValueError):c.analyze(self.r,self.s)

    def test_future_registry_requires_retrospective(self):
        self.r['available_at']='2026-10-30T00:00:00Z'
        with self.assertRaises(ValueError):c.analyze(self.r,self.s)
        self.assertEqual(c.analyze(self.r,self.s,retrospective=True)['replay_class'],'retrospective_diagnostic')

    def test_misaligned_relative_is_missing(self):
        self.s['quotes']['QQQ']['observed_at']='2026-10-29T15:55:00Z'
        self.assertIsNone(c.analyze(self.r,self.s)['tickers'][0]['relative_qqq_pp'])

    def test_baseline_mismatch_not_relative(self):
        self.s['quotes']['QQQ']['baseline_id']='different'
        self.assertIsNone(c.analyze(self.r,self.s)['tickers'][0]['relative_qqq_pp'])

    def test_common_universe_avoids_composition_delta(self):
        prior=snapshot('2026-10-29T15:00:00Z');del prior['quotes']['B'];prior['quotes']['A']['price']=100
        out=c.analyze(self.r,self.s,prior)
        self.assertAlmostEqual(out['interval']['observed_subset_mean_pct'],10);self.assertIsNone(out['interval']['basket_mean_pct'])
        self.assertEqual(out['interval']['common_tickers'],['A'])

    def test_future_previous_rejected(self):
        with self.assertRaises(ValueError):c.analyze(self.r,self.s,snapshot('2026-10-29T17:00:00Z'))

    def test_windows_require_same_session_and_alignment(self):
        old=snapshot('2026-10-29T15:00:00Z')
        out=c.window_deltas(self.r,self.s,[old]);self.assertEqual(out['5m']['state'],'missing_aligned_baseline');self.assertEqual(out['60m']['elapsed_seconds'],3600)

    def test_no_cross_session_open_vwap(self):
        self.s['session']='premarket'
        for q in self.s['quotes'].values():q['session']='premarket'
        self.assertIsNone(c.analyze(self.r,self.s)['tickers'][0]['above_vwap_pct'])

    def test_refresh_plan_full_membership(self):
        plan=c.refresh_plan(self.r);self.assertEqual(plan['expected_tickers'],['A','B','QQQ','SOXX'])

    def observations(self):
        return [{'metric_id':m['id'],'value':0,'unit':m['unit'],'observed_at':'2026-10-28T16:00:00Z','available_at':'2026-10-29T10:00:00Z','expires_at':'2026-10-30T20:00:00Z','status':'valid','evidence_class':'verified_observation','source':'synthetic_fixture'} for m in self.policy['scoring_matrix']]

    def test_macro_missing_gate(self):
        out=c.macro_score(self.policy,[],self.s['as_of']);self.assertIsNone(out['score']);self.assertEqual(len(out['missing_metrics']),21)

    def test_macro_unit_future_expiry_and_boundary(self):
        obs=self.observations();hy=next(o for o in obs if o['metric_id']=='hy_oas');hy['value']=350
        out=c.macro_score(self.policy,obs,self.s['as_of']);self.assertEqual(out['metric_scores']['hy_oas'],1);self.assertIsNotNone(out['score'])
        hy['expires_at']='2026-10-29T15:00:00Z';self.assertIn('hy_oas',c.macro_score(self.policy,obs,self.s['as_of'])['missing_metrics'])
        hy['expires_at']='2026-10-30T15:00:00Z';hy['unit']='percent';self.assertIn('hy_oas',c.macro_score(self.policy,obs,self.s['as_of'])['missing_metrics'])

    def test_growth_shock_caps_false_good_yield_signal(self):
        obs=self.observations();v={'qqq_return_5d':-5,'hy_oas_delta_5d':40,'nominal10y_delta_5d':-25,'wti_return_5d':-15}
        for o in obs:o['value']=v.get(o['metric_id'],0)
        out=c.macro_score(self.policy,obs,self.s['as_of']);self.assertIn('growth_shock',out['stress_flags']);self.assertEqual(out['metric_scores']['wti_return_5d'],0);self.assertEqual(out['raw_metric_scores']['wti_return_5d'],2)

    def test_macro_policy_bad_weights_rejected(self):
        self.policy['pillars'][0]['weight']=21
        with self.assertRaises(ValueError):c.macro_score(self.policy,[],self.s['as_of'])

    def test_macro_impulse_missing_not_zero(self):
        out=c.macro_score(self.policy,[],self.s['as_of']);self.assertIsNone(c.macro_impulse(self.policy,out,out)['score'])

    def test_nonfinite_rejected(self):
        for value in (float('nan'),float('inf'),True):
            with self.assertRaises(ValueError):c.number(value)

    def test_normalizer_detects_reset_snapshot(self):
        text='ticker,session_last_updated,session_price,session_previous_close,session_volume,last_minute_last_updated,last_minute_close\nA,1793289600000000000,100,100,10,1793289600000000000,110\n'
        out=c.normalize_massive(text,'2026-10-29T16:00:00Z','premarket');self.assertIn('snapshot_bar_conflict',out['quotes']['A']['quality_flags'])

    def test_journal_restart_duplicate_and_collision(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'journal.sqlite';j=c.Journal(path);j.append(self.s);j.append(self.s)
            self.assertEqual(j.db.execute('SELECT count(*) FROM snapshots').fetchone()[0],1)
            bad=copy.deepcopy(self.s);bad['quotes']['A']['price']=111
            with self.assertRaises(ValueError):j.append(bad)
            j.db.close();j=c.Journal(path);self.assertEqual(j.replay(self.s['as_of'],self.s['as_of'])['quotes']['A']['price'],110)

    def test_correction_no_lookahead_and_fork_rejection(self):
        j=c.Journal(':memory:');j.append(self.s);rev=copy.deepcopy(self.s);rev.update(snapshot_id='revision',available_at='2026-10-29T17:00:00Z',ingested_at='2026-10-29T17:00:00Z',supersedes=self.s['snapshot_id']);rev['quotes']['A']['price']=111;j.append(rev)
        self.assertEqual(j.replay(self.s['as_of'],self.s['as_of'])['quotes']['A']['price'],110)
        self.assertEqual(j.replay(self.s['as_of'],'2026-10-29T17:00:00Z')['quotes']['A']['price'],111)
        fork=copy.deepcopy(rev);fork.update(snapshot_id='fork',available_at='2026-10-29T18:00:00Z',ingested_at='2026-10-29T18:00:00Z')
        with self.assertRaises(ValueError):j.append(fork)
        self.assertEqual(j.db.execute('SELECT count(*) FROM snapshots').fetchone()[0],2)

    def test_captured_sessions_replay(self):
        fixtures=ROOT.parents[2]/'research/composites/market_context/fixtures'
        reg=c.read(fixtures.parent/'registry.working.json')
        out=c.analyze(reg,c.read(fixtures/'midday.json'),c.read(fixtures/'premarket.json'),'research',self.policy,True)
        crwv=next(r for r in out['tickers'] if r['ticker']=='CRWV')
        self.assertAlmostEqual(crwv['return_since_previous_pct'],7.398648648648631)
        self.assertEqual(crwv['state'],'recovering_outperformer');self.assertIsNone(out['daily']['basket_mean_pct'])

    def test_full_capture_keeps_unresolved_denominator(self):
        fixtures=ROOT.parents[2]/'research/composites/market_context/fixtures'
        reg=c.read(fixtures.parent/'registry.working.json')
        out=c.analyze(reg,c.read(fixtures/'basket.json'),c.read(fixtures/'midday.json'),'research',self.policy)
        self.assertEqual(out['daily']['expected'],66);self.assertEqual(out['daily']['covered'],65)
        self.assertIsNone(out['interval']['basket_mean_pct']);self.assertIsNone(out['macros']['score'])
        strict=c.analyze(reg,c.read(fixtures/'basket.json'),mode='strict',policy=self.policy)
        self.assertIsNone(strict['daily']['basket_mean_pct'])


if __name__=='__main__':unittest.main()
