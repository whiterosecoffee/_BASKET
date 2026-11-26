import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from patterns import (MINUTE, clock, update, detect, score, path, rvol, nearest,
                      boundary_state, boundary_step, baseline)
from store import capture, connect, export, export_input
from poller import aggregates, health, cycle

START = clock('2026-10-27T09:30:00-04:00')


def bar(i, close=60., opening=None, volume=1000, start=START, high=None, low=None):
    o = close if opening is None else opening
    return {'t': start+i*MINUTE, 'o': o, 'c': close, 'h': max(o,close)+.01 if high is None else high,
            'l': min(o,close)-.01 if low is None else low, 'vw': (o+close)/2, 'v': volume}


def waves(n=60):
    # Narrow candles with recurrent separated upper/lower pivots.
    prices = [60,60.3,60.6,60.3,60,59.7,59.4,59.7]
    return [bar(i, prices[i%8]) for i in range(n)]


def batch(rows=None, ticker='CRWV'):
    return {'ticker': ticker, 'bars': rows or waves(), 'daily': [], 'profiles': [], 'patterns': [],
            'source': {'source_id':'test', 'provider':'synthetic', 'entitlement':'fixture',
                       'observation_kind':'historical', 'retrieved_at':'2026-10-28T20:00:00Z',
                       'adjustment':'none', 'available_at':None}}


class Lifecycle(unittest.TestCase):
    def test_confirmed_pivots_freeze_without_future(self):
        b = batch(waves(35))
        _, a = update(b, START+30*MINUTE)
        b['bars'][-1]['c'] = 500
        b['bars'][-1]['h'] = 501
        _, again = update(b, START+30*MINUTE)
        self.assertEqual(a, again)
        self.assertIsNotNone(a[-1]['active_range'])
        self.assertEqual(a[-1]['active_range']['definition']['frozen_at'], START+30*MINUTE)

    def test_frozen_bands_unchanged_through_evaluation(self):
        b = batch()
        _, a = update(b, START+60*MINUTE)
        z = [s['active_range'] for s in a if s['active_range']]
        first = z[0]['definition']
        self.assertTrue(all(x['definition'] == first for x in z if x['id']==z[0]['id']))

    def test_break_two_closes_and_not_same_bar(self):
        rows = waves(30)+[bar(30,61),bar(31,61.1)]
        _, signals = update(batch(rows), START+32*MINUTE)
        self.assertEqual(signals[-2]['classification'], 'above_range_break_unconfirmed')
        self.assertEqual(signals[-1]['classification'], 'confirmed_break_up')
        self.assertIsNone(signals[-1]['active_range'])

    def test_no_contact_is_not_rejection(self):
        rows = waves(30)+[bar(i,60.1-.02*(i-30)) for i in range(30,37)]
        _, s = update(batch(rows), START+37*MINUTE)
        self.assertEqual(s[-1]['classification'], 'drifting_lower_ceiling_untested_5m')
        self.assertEqual(s[-1]['active_range']['boundaries']['upper']['retreats'], 0)

    def test_adjacent_contacts_debounce_and_real_retreat(self):
        state = boundary_state()
        for i in range(3):
            boundary_step(state, bar(i,60.95,high=61.01,low=60.94), [60.9,61], 'upper', 1)
        events = boundary_step(state,bar(3,60.5),[60.9,61],'upper',1)
        self.assertEqual(state['contacts'],1)
        self.assertEqual(state['retreats'],1)
        self.assertEqual(events[0]['kind'],'upper_retreated_after_contact')

    def test_same_bar_order_is_ambiguous(self):
        state = boundary_state()
        events = boundary_step(state,bar(0,60.5,high=61.01,low=60.49),[60.9,61],'upper',1)
        self.assertIn('ambiguous',events[-1]['kind'])
        self.assertEqual(state['retreats'],0)

    def test_gap_invalidates_active_zone(self):
        rows=waves(35);del rows[31]
        _,s=update(batch(rows),START+35*MINUTE)
        self.assertTrue(any(e['kind']=='range_invalidated_data_gap' for x in s for e in x['events']))
        self.assertIsNone(s[-1]['flow_15m'])

    def test_close_traversal_has_elapsed_time(self):
        rows=waves(30)+[bar(30,59.39),bar(31,60),bar(32,60.61)]
        _,s=update(batch(rows),START+33*MINUTE)
        legs=[e for x in s for e in x['events'] if e['kind'].startswith('close_traversal')]
        self.assertEqual(legs[0]['kind'],'close_traversal_up')
        self.assertEqual(legs[0]['minutes'],2)


class Metrics(unittest.TestCase):
    def test_symmetry_one_ratio_and_inverse(self):
        zone={'lower':[59,59.1],'upper':[60.9,61]}
        rows=[bar(i,60.2 if i%2==0 else 60,volume=1000) for i in range(14)]
        a=score(rows,zone,60)
        # Dollar prices differ slightly; use constant notional to isolate travel arithmetic.
        for b in rows:b['v']=100000/b['vw']
        a=score(rows,zone,60)
        self.assertAlmostEqual(a['ratio'],1)
        for i,b in enumerate(rows):
            if i%2==0:b['v']*=2
        self.assertAlmostEqual(score(rows,zone,60)['ratio'],.5)

    def test_one_sided_sample_null(self):
        self.assertIsNone(score([bar(i,60+i*.01) for i in range(15)],{'lower':[59,59.1],'upper':[61,61.1]},59.99)['ratio'])

    def test_path_monotone_and_roundtrip(self):
        self.assertAlmostEqual(path([bar(0,60.1,60),bar(1,60.2,60.1)],1)['signed_efficiency'],1)
        self.assertEqual(path([bar(0,60.1,60),bar(1,60,60.1)],1)['signed_efficiency'],0)
        self.assertIsNone(path([bar(0),bar(2)],1)['signed_efficiency'])

    def test_actual_same_clock_profile(self):
        profiles=[]
        for day in range(20,25):
            start=clock(f'2026-10-{day}T09:30:00-04:00')
            profiles += [bar(i,volume=100,start=start) for i in range(390)]
        self.assertEqual(rvol([bar(i,volume=200) for i in range(15)],profiles,'2026-10-27')['ratio'],2)
        self.assertIsNone(rvol([bar(0)],profiles[:390],'2026-10-27')['ratio'])

    def test_adv_needs_twenty_completed_prior_dates(self):
        self.assertIsNone(baseline([], '2026-10-27')['adv20'])
        daily=[bar(0,start=clock(f'2026-09-{i:02d}T00:00:00-04:00')) for i in range(1,21)]
        daily.append(bar(0,start=START,volume=1000000))
        self.assertEqual(baseline(daily,'2026-10-27')['adv20'],1000)

    def test_historical_matching_excludes_future_unknown_and_other_ticker(self):
        def record(event,ticker='CRWV',end='2026-10-26T11:00:00-04:00',available='2026-10-26T11:01:00-04:00'):
            return {'event_id':event,'ticker':ticker,'evaluated_through':end,
                    'quality':{'right_censored':False,'available_at':available},
                    'features_at_freeze':{'start_position':.5,'formation_flow':{'score':1},'formation_path':{'signed_efficiency':0}},
                    'outcome':{'first_passage':{'outcome':'timeout'}}}
        rows=[record('past'),record('future',end='2026-10-28T11:00:00-04:00'),record('unknown',available=None),record('other',ticker='NVDA')]
        self.assertEqual([r['event_id'] for r in nearest(rows,'CRWV',START,[.5,1,0])],['past'])
        self.assertEqual(len(nearest(rows,'CRWV',START,[.5,1,0],True)),2)
        rows[0]['outcome']['first_passage']['outcome']='changed'
        self.assertEqual(nearest(rows,'CRWV',START,[.5,1,0])[0]['distance'],0)


class Persistence(unittest.TestCase):
    def test_restart_equals_full_replay_and_duplicates_zero(self):
        b=batch()
        state,first=update(b,START+40*MINUTE)
        state,rest=update(b,START+60*MINUTE,state)
        whole,allrows=update(b,START+60*MINUTE)
        self.assertEqual(first+rest,allrows);self.assertEqual(state,whole)
        _,duplicate=update(b,START+60*MINUTE,state)
        self.assertEqual(duplicate,[])

    def test_revision_fails_and_old_state_preserved(self):
        b=batch();state,_=update(b,START+40*MINUTE);original=copy.deepcopy(state)
        b['bars'][0]['v']+=1
        with self.assertRaisesRegex(ValueError,'revised'):update(b,START+60*MINUTE,state)
        self.assertEqual(state,original)

    def test_prior_context_revision_requires_new_generation(self):
        b=batch();state,_=update(b,START+40*MINUTE)
        b['source']['adjustment']='revised'
        with self.assertRaisesRegex(ValueError,'context revised'):update(b,START+60*MINUTE,state)

    def test_retrieval_only_changes_do_not_reemit(self):
        b=batch();state,_=update(b,START+40*MINUTE)
        b['source']['retrieved_at']='2026-10-28T21:00:00Z'
        _,signals=update(b,START+40*MINUTE,state)
        self.assertEqual(signals,[])

    def test_transaction_rebuild_export_and_immutability(self):
        with tempfile.TemporaryDirectory() as td:
            db=Path(td)/'tape.sqlite';b=batch()
            self.assertEqual(capture(db,b,START+40*MINUTE)['new_signals'],40)
            self.assertEqual(capture(db,b,START+40*MINUTE)['new_signals'],0)
            b['bars'][0]['v']+=1
            with self.assertRaises(ValueError):capture(db,b,START+60*MINUTE)
            with connect(db) as c:self.assertEqual(c.execute('SELECT count(*) FROM signals').fetchone()[0],40)
            result=capture(db,b,START+40*MINUTE,rebuild=True)
            self.assertEqual(result['generation'],2)
            self.assertIsNotNone(result['latest']['supersedes_signal_id'])
            with connect(db) as c:
                with self.assertRaises(sqlite3.IntegrityError):c.execute('DELETE FROM signals')
            out=Path(td)/'signals.jsonl';export(db,'CRWV',out)
            self.assertEqual(len(out.read_text().splitlines()),80)

    def test_replay_from_captured_local_input_without_original_file(self):
        with tempfile.TemporaryDirectory() as td:
            db=Path(td)/'a.sqlite';other=Path(td)/'b.sqlite';out=Path(td)/'input.json'
            first=capture(db,batch(),START+40*MINUTE)
            export_input(db,'CRWV',out)
            second=capture(other,json.loads(out.read_text()),START+40*MINUTE)
            self.assertEqual(first['latest'],second['latest'])

    def test_cross_ticker_isolation(self):
        with tempfile.TemporaryDirectory() as td:
            db=Path(td)/'t.sqlite'
            capture(db,batch(),START+35*MINUTE)
            other=capture(db,batch(ticker='NVDA'),START+35*MINUTE)
            self.assertEqual(other['generation'],1)
            self.assertEqual(other['latest']['ticker'],'NVDA')

    def test_stale_historical_and_future_cutoff(self):
        b=batch();_,s=update(b,START+35*MINUTE)
        self.assertEqual(s[-1]['freshness'],'historical')
        self.assertFalse(s[-1]['point_in_time_verified'])
        self.assertGreater(s[-1]['lag_seconds_at_retrieval'],120)
        self.assertEqual(s[-1]['as_of'],START+35*MINUTE)


class Adapter(unittest.TestCase):
    def test_pagination_and_untrusted_redirect(self):
        calls=[]
        def fetch(path,params,key):
            calls.append(path)
            return {'results':[bar(len(calls)-1)], **({'next_url':'https://api.massive.com/v2/aggs/ticker/CRWV/range/1/minute/a/b?cursor=x'} if len(calls)==1 else {})}
        self.assertEqual(len(aggregates('CRWV','a','b','redacted',fetch)),2)
        def bad(*args):return {'next_url':'https://evil.test/steal'}
        with self.assertRaises(ValueError):aggregates('CRWV','a','b','redacted',bad)

    def test_missing_and_feed_health(self):
        self.assertFalse(health(100000,True,None,'realtime_verified')['fresh_for_current_inference'])
        self.assertFalse(health(100000,True,90000,'delay_unknown')['fresh_for_current_inference'])
        self.assertTrue(health(100000,True,90000,'realtime_verified')['fresh_for_current_inference'])
        self.assertEqual(health(100000,False,0,'realtime_verified')['state'],'market_closed')

    def test_bounded_pagination_and_provider_failure(self):
        def bad(*args):return {'status':'NOT_ENTITLED'}
        with self.assertRaises(RuntimeError):aggregates('CRWV','a','b','redacted',bad)
        count=[0]
        def endless(*args):
            count[0]+=1
            return {'next_url':f'https://api.massive.com/v2/aggs/ticker/CRWV/range/1/minute/a/b?cursor={count[0]}'}
        with self.assertRaisesRegex(ValueError,'bounded'):aggregates('CRWV','a','b','redacted',endless,max_pages=2)

    def test_poller_twice_restart_duplicate_safe(self):
        now=START+35*MINUTE
        def fetch(path,params,key):
            return {'market':'open'} if path=='/v1/marketstatus/now' else {'results':waves(35),'status':'OK'}
        with tempfile.TemporaryDirectory() as td:
            db=Path(td)/'t.sqlite'
            context={'daily':[],'profiles':[],'patterns':[]}
            a=cycle(db,'CRWV','redacted','delay_unknown',context,now,fetch)
            b=cycle(db,'CRWV','redacted','delay_unknown',context,now+1000,fetch)
            self.assertEqual(a['new_signals'],35)
            self.assertEqual(b['new_signals'],0)
            self.assertFalse(b['fresh_for_current_inference'])


if __name__=='__main__':unittest.main()
