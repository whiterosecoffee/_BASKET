import json
import subprocess
import sys
import tempfile
import unittest
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

spec=spec_from_file_location("metrics",Path(__file__).resolve().parents[1]/"metrics.py")
m=module_from_spec(spec);spec.loader.exec_module(m)

def bars(name="CRWV", n=40):
    return [{"t":i*60000,"o":100+i*.01,"h":100.05+i*.01,
             "l":99.95+i*.01,"c":100.02+i*.01,"v":100,
             "vw":100+i*.01} for i in range(n)]

class TestMetrics(unittest.TestCase):
    def test_ticker_isolation_and_prefix(self):
        x=m.evaluate("CRWV",bars())
        y=m.evaluate("ORCL",bars())
        self.assertEqual(x["windows"],y["windows"])
        self.assertNotEqual(x["instrument"],y["instrument"])
        # Streaming a one-pass iterable and replaying its completed prefix
        # must yield the same descriptive snapshot as a materialized batch.
        for n in (5, 15, 20, 39, 40):
            source = bars()[:n]
            self.assertEqual(m.evaluate("CRWV", iter(source)),
                             m.evaluate("CRWV", source))
    def test_intraday_ranges_and_nulls(self):
        x=m.evaluate("CRWV",bars())
        self.assertIsNotNone(x["windows"]["15m"])
        self.assertIsNone(x["windows"]["60m"])
        self.assertIsNone(x["windows"]["15m"]["directional_efficiency_ratio"])
        self.assertIsNone(x["windows"]["15m"]["same_clock_rvol"])
        self.assertIsNone(x["windows"]["15m"]["normalized_position_velocity"])
    def test_reject_duplicate(self):
        with self.assertRaises(ValueError): m.evaluate("CRWV",bars()+bars()[-1:])
    def test_reject_partial(self):
        with self.assertRaises(ValueError): m.evaluate("CRWV",bars(),as_of=39*60000+1)
    def test_reject_gap_window(self):
        b=bars();b[-1]["t"]+=60000
        self.assertIsNone(m.evaluate("CRWV",b)["windows"]["5m"])
    def test_turnover_and_path(self):
        x=m.evaluate("CRWV",bars( n=16))["windows"]["15m"]
        self.assertGreater(x["estimated_turnover_usd"],0)
        self.assertTrue(0<=x["position"]<=1)
        self.assertGreater(x["net_progress_usd"],0)


    def test_sampled_path_first_candle_and_sign(self):
        for sign in (1, -1):
            b = []
            for i in range(5):
                o = 100 if i == 0 else 100 + sign*(9+i)
                close = 100 + sign*(10+i)
                b.append(dict(t=i*60000,o=o,c=close,h=max(o,close),
                              l=min(o,close),v=100,vw=close))
            for ticker in ("CRWV","ORCL"):
                x=m.evaluate(ticker,b,as_of=300000)["windows"]["5m"]
                self.assertEqual(x["net_progress_usd"],sign*14)
                self.assertAlmostEqual(x["path_efficiency"],float(sign))

    def test_first_candle_only_and_round_trip(self):
        b=[dict(t=i*60000,o=100 if i==0 else 110,c=110,
                h=110,l=100 if i==0 else 110,v=100) for i in range(5)]
        self.assertEqual(m.evaluate("CRWV",b)["windows"]["5m"]["path_efficiency"],1)
        closes=[110,105,100,105,100]
        opens=[100]+closes[:-1]
        q=[dict(t=i*60000,o=o,c=close,h=max(o,close),l=min(o,close),v=100)
           for i,(o,close) in enumerate(zip(opens,closes))]
        w=m.evaluate("ORCL",q)["windows"]["5m"]
        self.assertEqual(w["net_progress_usd"],0)
        self.assertEqual(w["path_efficiency"],0)

    def test_flat_path_null_and_partial_clock_baseline(self):
        b=[dict(t=i*60000,o=100,c=100,h=100,l=100,v=100) for i in range(5)]
        x=m.evaluate("CRWV",b,same_clock_expected={15:1000})["windows"]["5m"]
        self.assertIsNone(x["path_efficiency"])
        self.assertIsNone(x["same_clock_rvol"])
        self.assertEqual(m.evaluate("CRWV",b,same_clock_expected={5:250})["windows"]["5m"]["same_clock_rvol"],2)

    def test_first_candle_gap_does_not_fabricate_efficiency(self):
        b=[dict(t=i*60000,o=100 if i==0 else 110,c=110,
                h=110,l=100 if i==0 else 110,v=100) for i in range(5)]
        b[-1]["t"] += 60000
        self.assertIsNone(m.evaluate("CRWV",b)["windows"]["5m"])


    def test_sampled_path_is_defined_for_every_complete_horizon(self):
        for sign in (1, -1):
            source = [dict(t=i*60000, o=1000+sign*i,
                           c=1000+sign*(i+1),
                           h=max(1000+sign*i, 1000+sign*(i+1)),
                           l=min(1000+sign*i, 1000+sign*(i+1)), v=100)
                      for i in range(390)]
            for ticker in ("CRWV", "ORCL"):
                output = m.evaluate(ticker, source, as_of=390*60000)
                for minutes in (5, 15, 60, 390):
                    with self.subTest(sign=sign, ticker=ticker, minutes=minutes):
                        window = output["windows"][str(minutes)+"m"]
                        self.assertEqual(window["net_progress_usd"], sign*minutes)
                        self.assertEqual(window["path_efficiency"], sign)

    def test_single_bar_window_uses_open_to_close_path(self):
        # No close-to-close pair exists; first-candle travel is still defined.
        for close, expected in ((110, 1), (90, -1), (100, None)):
            with self.subTest(close=close):
                source = [dict(t=0, o=100, c=close, h=max(100, close),
                               l=min(100, close), v=100)]
                window = m.evaluate("CRWV", source, interval_minutes=5,
                                    as_of=300000)["windows"]["5m"]
                self.assertEqual(window["path_efficiency"], expected)

    def test_cli_emits_same_complete_window_snapshot_as_api(self):
        source = bars(n=15)
        script = Path(__file__).resolve().parents[1]/"run_metrics.py"
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory)/"completed-bars.jsonl"
            input_path.write_text("".join(json.dumps(row)+"\n" for row in source))
            completed = subprocess.run(
                [sys.executable, "-B", str(script), "ORCL", "--jsonl", str(input_path),
                 "--interval", "1", "--as-of-ms", "900000"],
                text=True, capture_output=True, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout),
                         m.evaluate("ORCL", source, as_of=900000))

    def test_reject_nonfinite_observation_fields(self):
        for field in ("o", "h", "l", "c", "v", "vw"):
            for value in (float("nan"), float("inf"), float("-inf")):
                for legacy in (False, True):
                    with self.subTest(field=field, value=value, legacy=legacy):
                        source = bars(n=5)
                        source[2][field] = value
                        if legacy:
                            source = [[row[k] for k in ("t", "o", "h", "l", "c", "v", "vw")] + [0]
                                      for row in source]
                        with self.assertRaises(ValueError):
                            m.evaluate("CRWV", source)

    def test_reject_boolean_numeric_observations(self):
        for field in ("v", "vw"):
            with self.subTest(field=field):
                source = bars(n=5)
                source[2][field] = True
                with self.assertRaises(ValueError):
                    m.evaluate("ORCL", source)

    def test_reject_noninteger_bar_start_without_coercion(self):
        for value in (0.5, 0.0, True, "0", float("nan"), float("inf")):
            for legacy in (False, True):
                with self.subTest(value=value, legacy=legacy):
                    source = bars(n=5)
                    source[0]["t"] = value
                    if legacy:
                        source = [[row[k] for k in ("t", "o", "h", "l", "c", "v", "vw")] + [0]
                                  for row in source]
                    with self.assertRaises(ValueError):
                        m.evaluate("ORCL", source)

    def test_interval_and_cutoff_require_integers(self):
        for interval in (True, 1.0, "1", float("nan"), float("inf"), 0, -1):
            with self.subTest(interval=interval):
                with self.assertRaises(ValueError):
                    m.evaluate("CRWV", bars(n=5), interval_minutes=interval)
        for cutoff in (True, 300000.5, "300000", float("nan"), float("inf")):
            with self.subTest(cutoff=cutoff):
                with self.assertRaises(ValueError):
                    m.evaluate("CRWV", bars(n=5), as_of=cutoff)

    def test_optional_volume_profiles_must_be_finite(self):
        for value in (float("nan"), float("inf"), float("-inf"), True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    m.evaluate("CRWV", bars(n=5), prior_20_session_adv=value)
                with self.assertRaises(ValueError):
                    m.evaluate("CRWV", bars(n=5), same_clock_expected={5: value})

    def test_fractional_volume_outside_range_vwap_and_nulls_survive(self):
        source = bars(n=5)
        for row in source:
            row.update(v=100.25, vw=200)
        legacy = [[row[k] for k in ("t", "o", "h", "l", "c", "v", "vw")] + [0]
                  for row in source]
        original = json.dumps(source, sort_keys=True)
        for ticker in ("CRWV", "ORCL"):
            result = m.evaluate(ticker, source, prior_20_session_adv=0,
                                same_clock_expected={5: 0})
            self.assertEqual(result, m.evaluate(ticker, legacy, prior_20_session_adv=0,
                                               same_clock_expected={5: 0}))
            window = result["windows"]["5m"]
            self.assertEqual(window["shares"], 501.25)
            self.assertEqual(window["estimated_turnover_usd"], 100250)
            self.assertIsNone(window["prior_20_session_adv_pct"])
            self.assertIsNone(window["same_clock_rvol"])
            self.assertIsNone(result["windows"]["15m"])
            self.assertEqual(json.loads(json.dumps(result, allow_nan=False)), result)
        self.assertEqual(json.dumps(source, sort_keys=True), original)

    def test_finite_inputs_cannot_emit_overflowed_metrics(self):
        source = bars(n=5)
        for row in source:
            row["v"] = 1e308
        with self.assertRaises(ValueError):
            m.evaluate("CRWV", source)

    def test_cli_rejects_nonfinite_volume_without_emitting_snapshot(self):
        source = bars(n=5)
        source[2]["v"] = float("nan")
        script = Path(__file__).resolve().parents[1]/"run_metrics.py"
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory)/"invalid-bars.jsonl"
            input_path.write_text("".join(json.dumps(row)+"\n" for row in source))
            completed = subprocess.run(
                [sys.executable, "-B", str(script), "CRWV", "--jsonl", str(input_path)],
                text=True, capture_output=True, timeout=10)
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertIn("finite number", completed.stderr)

if __name__=="__main__":unittest.main()
