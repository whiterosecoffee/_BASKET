"""Source-time regressions: a later evaluation is not a later observation."""
import copy
import unittest

from test_context import c, registry, snapshot


class ObservationFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.previous = snapshot()
        self.current = copy.deepcopy(self.previous)
        self.current.update(snapshot_id="later-capture", as_of="2026-10-29T16:01:00Z",
                            available_at="2026-10-29T16:01:00Z",
                            ingested_at="2026-10-29T16:01:00Z")

    def test_later_capture_does_not_manufacture_zero_returns(self):
        for mode in ("strict", "research"):
            with self.subTest(mode=mode):
                self.assertEqual(c.comparison(self.current, self.previous, mode), {})
                out = c.analyze(registry(), self.current, self.previous, mode)
                self.assertEqual(out["interval"]["coverage"], 0)
                self.assertIsNone(out["interval"]["basket_mean_pct"])
                self.assertEqual(out["interval"]["common_tickers"], [])
                self.assertEqual(out["interval"]["elapsed_seconds"], 60)
                self.assertEqual(out["interval"]["baseline_snapshot_id"], self.previous["snapshot_id"])
                for row in out["tickers"]:
                    self.assertEqual(row["interval_status"], "no_new_observation")
                    self.assertIsNone(row["return_since_previous_pct"])
                    self.assertIsNone(row["relative_qqq_since_previous_pp"])
                detail = out["interval"]["comparisons"]["A"]
                self.assertEqual(detail["current_observation"]["observed_at"], self.previous["as_of"])
                self.assertEqual(detail["baseline_observation"]["source"], "test_fixture")
                self.assertEqual(detail["observation_elapsed_seconds"], 0)
                # Prior-close arithmetic still describes the retained observation.
                self.assertEqual(out["daily"]["coverage"], 1)

    def test_capture_and_availability_changes_do_not_refresh_observation(self):
        for quote in self.current["quotes"].values():
            quote["available_at"] = self.current["available_at"]
        self.assertEqual(c.comparison(self.current, self.previous, "strict"), {})
        self.assertEqual(c.comparison_details(self.current, self.previous, "strict")["A"]["status"],
                         "no_new_observation")

    def test_new_observation_with_unchanged_price_is_measured_zero(self):
        self.current = snapshot("2026-10-29T16:01:00Z")
        self.assertEqual(c.comparison(self.current, self.previous, "strict"),
                         {"A": 0.0, "B": 0.0, "QQQ": 0.0, "SOXX": 0.0})
        detail = c.comparison_details(self.current, self.previous, "strict")["A"]
        self.assertEqual(detail["status"], "valid")
        self.assertEqual(detail["observation_elapsed_seconds"], 60)

    def test_partial_refresh_keeps_full_denominator_and_missing_benchmark(self):
        self.current["quotes"]["A"].update(price=121, observed_at=self.current["as_of"],
                                            available_at=self.current["available_at"])
        out = c.analyze(registry(), self.current, self.previous)
        self.assertAlmostEqual(out["tickers"][0]["return_since_previous_pct"], 10)
        self.assertIsNone(out["tickers"][0]["relative_qqq_since_previous_pp"])
        self.assertEqual(out["interval"]["coverage"], .5)
        self.assertIsNone(out["interval"]["basket_mean_pct"])
        self.assertEqual(out["interval"]["common_tickers"], ["A"])

    def test_same_time_revision_is_not_market_movement(self):
        self.current["quotes"]["A"].update(price=111, revision_id="correction-2")
        detail = c.comparison_details(self.current, self.previous, "strict")["A"]
        self.assertEqual(detail["status"], "observation_revision")
        self.assertIsNone(detail["return_pct"])
        self.assertEqual(detail["current_observation"]["revision_id"], "correction-2")
        self.assertNotIn("A", c.comparison(self.current, self.previous, "strict"))

    def test_regressed_source_time_is_not_forward_return(self):
        self.current["quotes"]["A"]["observed_at"] = "2026-10-29T15:59:30Z"
        detail = c.comparison_details(self.current, self.previous, "strict")["A"]
        self.assertEqual(detail["status"], "regressed_observation")
        self.assertIsNone(detail["return_pct"])

    def test_timezone_alias_does_not_create_new_observation(self):
        self.current["quotes"]["A"]["observed_at"] = "2026-10-29T12:00:00-04:00"
        self.assertEqual(c.comparison_details(self.current, self.previous, "strict")["A"]["status"],
                         "no_new_observation")

    def test_invalid_states_take_precedence_over_repeated_observation(self):
        for field, value, status in (("observed_at", "2026-10-29T16:02:00Z", "future"),
                                     ("observed_at", "2026-10-29T15:50:00Z", "stale"),
                                     ("quality_flags", ["conflict"], "conflicting_or_invalid"),
                                     ("entitlement", "unknown", "entitlement_unknown")):
            with self.subTest(status=status):
                current = copy.deepcopy(self.current)
                current["quotes"]["A"][field] = value
                detail = c.comparison_details(current, self.previous, "strict")["A"]
                self.assertEqual(detail["status"], "current_" + status)
                self.assertIsNone(detail["return_pct"])

    def test_basis_source_and_missing_baseline_remain_explicit(self):
        for field in ("basis", "source"):
            with self.subTest(field=field):
                current = snapshot("2026-10-29T16:01:00Z")
                current["quotes"]["A"][field] = "different"
                self.assertEqual(c.comparison_details(current, self.previous, "strict")["A"]["status"],
                                 field + "_mismatch")
        del self.previous["quotes"]["A"]
        self.assertEqual(c.comparison_details(self.current, self.previous, "strict")["A"]["status"],
                         "baseline_missing")

    def test_delayed_repeated_window_does_not_become_fresh_zero(self):
        self.current.update(as_of="2026-10-29T16:05:00Z", available_at="2026-10-29T16:05:00Z",
                            ingested_at="2026-10-29T16:05:00Z")
        for snap in (self.previous, self.current):
            for quote in snap["quotes"].values():
                quote.update(entitlement="delayed", delay_seconds=900)
        out = c.window_deltas(registry(), self.current, [self.previous], minutes=(5,))['5m']
        self.assertEqual(out["coverage"], 0)
        self.assertIsNone(out["basket_mean_pct"])
        self.assertEqual(out["comparisons"]["A"]["status"], "no_new_observation")

    def test_no_baseline_remains_empty_numeric_comparison(self):
        self.assertEqual(c.comparison(self.current, None, "strict"), {})
        out = c.analyze(registry(), self.current)
        self.assertEqual(out["tickers"][0]["interval_status"], "missing_baseline")
        self.assertIsNone(out["interval"]["elapsed_seconds"])


if __name__ == "__main__":
    unittest.main()
