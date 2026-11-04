"""Synthetic conformance tests only: no Massive IO, real session calendar, or alpha."""
import unittest
from datetime import date, timedelta
from reference_state import evaluate


def bars(n, *, start=100.0, step=0.0, available="2026-11-04T23:00:00Z"):
    origin = date(2024, 1, 1)
    return [
        dict(session_date=(origin + timedelta(days=i)).isoformat(),
             o=start+i*step, h=start+i*step+1, l=start+i*step-1,
             c=start+i*step, adjustment="split_adjusted",
             complete=True, available_at=available)
        for i in range(n)
    ]


def run(rows, cutoff="2026-11-04T23:59:00Z", **kwargs):
    return evaluate(rows, as_of=cutoff, instrument="TEST",
                    input_manifest_hash="fixture-sha", calendar_validated=True, **kwargs)


class HistoricalStateTests(unittest.TestCase):
    def test_sma_9_10(self):
        self.assertIsNone(run(bars(9))["features"]["10"]["sma"])
        self.assertEqual(run(bars(10))["features"]["10"]["sma"], 100)

    def test_sma_29_30(self):
        self.assertIsNone(run(bars(29))["features"]["30"]["sma"])
        self.assertEqual(run(bars(30))["features"]["30"]["sma"], 100)

    def test_slope_34_35(self):
        self.assertIsNone(run(bars(34))["features"]["30"]["slope_5_pct"])
        self.assertAlmostEqual(run(bars(35, step=1))["features"]["30"]["slope_5_pct"],
                               100*((119.5/114.5)-1))

    def test_sma_199_200(self):
        self.assertIsNone(run(bars(199))["features"]["200"]["sma"])
        self.assertEqual(run(bars(200))["features"]["200"]["sma"], 100)

    def test_slope_204_205(self):
        self.assertIsNone(run(bars(204))["features"]["200"]["slope_5_pct"])
        self.assertAlmostEqual(run(bars(205, step=1))["features"]["200"]["slope_5_pct"],
                               100*((204.5/199.5)-1))

    def test_rank_451_452(self):
        self.assertIsNone(run(bars(451))["features"]["200"]["rank_percentile"])
        result = run(bars(452))["features"]["200"]
        self.assertEqual(result["rank_prior_n"], 252)
        self.assertEqual(result["rank_percentile"], 50)

    def test_wilder_atr(self):
        self.assertIsNone(run(bars(14))["features"]["200"]["wilder_atr14"])
        self.assertEqual(run(bars(15))["features"]["200"]["wilder_atr14"], 2)
        self.assertEqual(run(bars(452))["features"]["200"]["wilder_atr14"], 2)

    def test_persistence_tie(self):
        result = run(bars(35))["features"]["30"]
        self.assertEqual(result["signed_persistence_sessions"], 0)
        self.assertFalse(result["left_censored"])

    def test_persistence_left_censor(self):
        state = run(bars(14, step=1))["features"]["10"]
        self.assertEqual(state["signed_persistence_sessions"], 5)
        self.assertTrue(state["left_censored"])

    def test_asof_no_future_close(self):
        rows = bars(35)
        rows[-1]["available_at"] = "2026-11-05T00:00:00Z"
        result = run(rows)
        self.assertEqual(result["eligible_completed_sessions"], 34)
        self.assertIsNone(result["features"]["30"]["slope_5_pct"])

    def test_incomplete_session_dropped(self):
        rows = bars(10)
        rows[-1]["complete"] = False
        self.assertIsNone(run(rows)["features"]["10"]["sma"])

    def test_exchange_local_date_can_lead_utc_date(self):
        row = bars(1)[0]
        row["session_date"] = "2026-11-05"
        row["available_at"] = "2026-11-04T22:30:00Z"
        result = run([row], cutoff="2026-11-04T23:00:00Z")
        self.assertEqual(result["eligible_completed_sessions"], 1)
        self.assertEqual(result["last_session"], "2026-11-05")

    def test_interior_unavailable_bar_fails_closed(self):
        rows = bars(35)
        rows[20]["available_at"] = "2026-11-05T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "non-prefix eligible"):
            run(rows)

    def test_interior_incomplete_bar_fails_closed(self):
        rows = bars(35)
        rows[20]["complete"] = False
        with self.assertRaisesRegex(ValueError, "non-prefix eligible"):
            run(rows)

    def test_future_tail_is_excluded_without_compression(self):
        rows = bars(35)
        for row in rows[30:]:
            row["available_at"] = "2026-11-05T00:00:00Z"
        state = run(rows)
        self.assertEqual(state["eligible_completed_sessions"], 30)
        self.assertIsNone(state["features"]["30"]["slope_5_pct"])

    def test_no_calendar_attestation(self):
        with self.assertRaises(ValueError):
            evaluate(bars(30), as_of="2026-11-04T23:59:00Z",
                     instrument="TEST", input_manifest_hash="sha")

    def test_no_source_hash(self):
        with self.assertRaises(ValueError):
            evaluate(bars(30), as_of="2026-11-04T23:59:00Z",
                     instrument="TEST", input_manifest_hash="", calendar_validated=True)

    def test_mixed_adjustment_fails(self):
        rows = bars(30)
        rows[-1]["adjustment"] = "unadjusted"
        with self.assertRaises(ValueError):
            run(rows)

    def test_duplicate_session_fails(self):
        rows = bars(12)
        rows[-1]["session_date"] = rows[-2]["session_date"]
        with self.assertRaises(ValueError):
            run(rows)

    def test_invalid_ohlc_fails(self):
        rows = bars(10)
        rows[-1]["h"] = 90
        with self.assertRaises(ValueError):
            run(rows)

    def test_naive_asof_fails(self):
        with self.assertRaises(ValueError):
            run(bars(10), cutoff="2026-11-04T23:59:00")

    def test_percent_vs_pp_separate(self):
        result = run(bars(35, step=1))
        d = result["features"]["30"]
        self.assertGreater(d["distance_pct"], 0)
        self.assertLess(d["approach_velocity_pp_per_session"], 0)
        self.assertEqual(result["status"], "descriptive_only")


if __name__ == "__main__":
    unittest.main()
