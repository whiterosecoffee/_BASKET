import copy, json, tempfile, unittest
from pathlib import Path
from battle_matrix import evaluate, append_snapshot, path_summary, boundary_summary
START=1793196000000
ASOF=START+15*60000

def fixture():
    bars=[]; price=60.
    for i in range(15):
        change=.2 if i%2==0 else -.1
        before=price; price+=change
        bars.append(dict(t=START+i*60000,o=before,c=price,h=max(before,price)+.01,
                         l=min(before,price)-.01,v=100.,vw=60.))
    # Calendar dates merely provide 20 prior sessions for deterministic unit tests.
    daily=[dict(t=1791345600000-i*86400000,o=60.,c=60.,h=61.,l=59.,v=10000.,vw=60.) for i in range(20)][::-1]
    return dict(as_of=ASOF,session="2026-10-28",config={"half_life_minutes":5,"min_directional_bars":3},
                tickers=[dict(ticker="TEST",bars=bars,daily=daily,
                             zones=[dict(id="z1",lower=[58.,59.],upper=[62.,63.],frozen_at=START)])])
def metrics(x):
    return evaluate(x)["rows"][0]["windows"]["15"]

class MatrixTests(unittest.TestCase):
    def test_straight_path(self):
        bars=fixture()['tickers'][0]['bars']
        for i,b in enumerate(bars): b.update(o=60+i*.1,c=60+(i+1)*.1)
        self.assertAlmostEqual(path_summary(bars,5)['signed_efficiency'],1.)
    def test_round_trip_is_zero_progress(self):
        bars=fixture()['tickers'][0]['bars'][:2]
        bars[0].update(o=60.,c=61.);bars[1].update(o=61.,c=60.)
        self.assertEqual(path_summary(bars,5)['signed_efficiency'],0.)
        self.assertEqual(path_summary(bars,5)['gross_travel_ranges'],.4)
    def test_down_path_negative(self):
        bars=fixture()['tickers'][0]['bars'][:1];bars[0].update(o=60.,c=59.)
        self.assertEqual(path_summary(bars,5)['signed_efficiency'],-1.)
    def test_gap_not_interpolated(self):
        bars=fixture()['tickers'][0]['bars'][:3];bars.pop(1)
        self.assertIsNone(path_summary(bars,5)['signed_efficiency'])
    def test_no_ceiling_attempt_is_not_rejection(self):
        bars=fixture()['tickers'][0]['bars']
        r=boundary_summary(bars,[62.,63.],5.,ASOF)
        self.assertTrue(r['no_ceiling_contact_in_window'])
        self.assertEqual(r['close_entry_episodes'],0)
    def test_contact_bars_not_independent_entries(self):
        bars=fixture()['tickers'][0]['bars'][:4]
        for b,c in zip(bars,[61.,62.1,62.2,62.1]): b.update(c=c,h=c+.1,l=c-.1)
        r=boundary_summary(bars,[62.,63.],5.,ASOF)
        self.assertEqual(r['contact_bar_count'],3)
        self.assertEqual(r['close_entry_episodes'],1)
    def test_initial_contact_left_censored(self):
        bars=fixture()['tickers'][0]['bars'][:1];bars[0].update(c=62.1,h=62.2,l=62.)
        r=boundary_summary(bars,[62.,63.],5.,ASOF)
        self.assertTrue(r['initial_inside_episode_left_censored'])
        self.assertEqual(r['close_entry_episodes'],0)
    def test_directional_ratio(self):
        self.assertAlmostEqual(metrics(fixture())["score"],2.,places=10)
    def test_turnover_weight(self):
        x=fixture()
        for i,b in enumerate(x["tickers"][0]["bars"]):
            if i%2==0: b["v"]*=2
        self.assertAlmostEqual(metrics(x)["score"],1.,places=10)
    def test_price_unit_scale_invariance(self):
        x=fixture(); y=copy.deepcopy(x)
        for b in y["tickers"][0]["bars"]+y["tickers"][0]["daily"]:
            for k in ("o","c","h","l","vw"): b[k]*=100
        for band in ("lower","upper"):
            y["tickers"][0]["zones"][0][band]=[p*100 for p in y["tickers"][0]["zones"][0][band]]
        self.assertAlmostEqual(metrics(x)["score"],metrics(y)["score"],places=10)
    def test_volume_unit_scale_invariance(self):
        x=fixture(); y=copy.deepcopy(x)
        for b in y["tickers"][0]["bars"]+y["tickers"][0]["daily"]: b["v"]*=100
        self.assertAlmostEqual(metrics(x)["score"],metrics(y)["score"],places=10)
        self.assertAlmostEqual(metrics(x)["volume_pct_adv20"],metrics(y)["volume_pct_adv20"])
    def test_prefix_replay(self):
        x=fixture(); expected=evaluate(x)
        b=copy.deepcopy(x["tickers"][0]["bars"][-1]); b["t"]+=60000
        x["tickers"][0]["bars"].append(b)
        self.assertEqual(evaluate(x),expected)
    def test_missing_baseline_is_not_one(self):
        x=fixture(); x["tickers"][0]["daily"]=x["tickers"][0]["daily"][:5]
        self.assertIsNone(metrics(x)["score"])
        self.assertEqual(metrics(x)["state"],"missing_baseline")
    def test_short_window_insufficient(self):
        self.assertIsNone(evaluate(fixture())["rows"][0]["windows"]["5"]["score"])
    def test_freeze_boundary(self):
        x=fixture(); x["tickers"][0]["zones"][0]["frozen_at"]=ASOF-4*60000
        self.assertFalse(metrics(x)["window_complete"])
        self.assertEqual(metrics(x)["eligible_window_minutes"],4)
        self.assertIsNone(metrics(x)["score"])
    def test_duplicate_rejected(self):
        x=fixture(); x["tickers"][0]["bars"].append(x["tickers"][0]["bars"][-1])
        with self.assertRaises(ValueError): evaluate(x)
    def test_multi_ticker_isolation(self):
        x=fixture(); y=copy.deepcopy(x["tickers"][0]); y["ticker"]="OTHER"
        for b in y["bars"]: b["v"]*=3
        x["tickers"].append(y)
        self.assertEqual(len(evaluate(x)["rows"]),2)
        self.assertAlmostEqual(evaluate(x)["rows"][0]["windows"]["15"]["score"],2.)
    def test_history_idempotence_and_revision(self):
        x=fixture(); out=evaluate(x)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"h.jsonl"
            self.assertTrue(append_snapshot(path,out))
            self.assertFalse(append_snapshot(path,out))
            x["tickers"][0]["bars"][-1]["v"]*=2
            revised=evaluate(x)
            self.assertTrue(append_snapshot(path,revised))
            records=[json.loads(s) for s in path.read_text().splitlines()]
            self.assertEqual(len(records),2)
            self.assertEqual(records[-1]["supersedes_snapshot_id"],out["snapshot_id"])
    def test_volumes_reconcile(self):
        m=metrics(fixture())
        self.assertAlmostEqual(m["assigned_dollar_volume"],
            sum(s["notional"] for s in m["sides"].values())+m["neutral_notional"])
if __name__=="__main__": unittest.main()

