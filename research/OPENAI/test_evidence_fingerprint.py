"""Offline B13 revision/fingerprint regressions; no provider credentials needed."""
import copy
import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("b13_evidence", HERE / "evidence_fingerprint.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FingerprintTests(unittest.TestCase):
    def setUp(self):
        self.v = mod.load("valuation-register.json")
        self.n = mod.load("ipo2027-news.json")
        self.p = mod.load("ipo2027-policy.json")
        self.r = mod.load("resource-registry.json")

    def snapshot(self):
        return mod.build("2026-10-17", valuation=self.v,
                         news=self.n, policy=self.p, resources=self.r)

    def test_deterministic_same_inputs(self):
        a = self.snapshot()
        b = self.snapshot()
        self.assertEqual(a, b)
        self.assertEqual(len(a["dependency_fingerprint"]), 64)
        self.assertEqual(a["temporal_precision"], "calendar_day")
        self.assertIsNone(a["ingested_at_utc"])
        self.assertIsNone(a["data_snapshot_hash"])
        self.assertNotIn("B09", a["record_kinds"].values())
        self.assertEqual(mod.compare(a, b)["recompute_consumer_sparks"], [])

    def test_input_order_is_irrelevant(self):
        a = self.snapshot()
        self.v["observations"].reverse()
        self.n["items"].reverse()
        self.r["sources"].reverse()
        self.assertEqual(a["dependency_fingerprint"],
                         self.snapshot()["dependency_fingerprint"])

    def test_new_economic_research_invalidates_b04_not_other_sparks(self):
        old = self.snapshot()
        row = copy.deepcopy(self.v["observations"][0])
        row["id"] = "OPENAI-CORRECTLY-DATED-NEW-EVIDENCE-001"
        row["measurement"] = "normalized_revenue_scenario_input_proxy"
        self.v["observations"].append(row)
        delta = mod.compare(old, self.snapshot())
        self.assertIn("valuation:" + row["id"], delta["added_input_ids"])
        self.assertIn("B04", delta["recompute_consumer_sparks"])
        self.assertIn("B09", delta["no_recompute_for_other_sparks"])
        self.assertTrue(delta["recompute_is_proposal_not_dispatched"])

    def test_derivative_does_not_trigger_parent_nav_recompute(self):
        old = self.snapshot()
        row = copy.deepcopy(next(x for x in self.v["observations"]
                                 if "perp" in x["measurement"]))
        row["id"] = "OPENAI-REPORTED-PERP-NEW-002"
        self.v["observations"].append(row)
        delta = mod.compare(old, self.snapshot())
        self.assertIn("B21", delta["recompute_consumer_sparks"])
        self.assertNotIn("B09", delta["recompute_consumer_sparks"])
        self.assertNotIn("B04", delta["recompute_consumer_sparks"])

    def test_real_stake_record_affects_parent_and_valuation_research(self):
        old = self.snapshot()
        row = copy.deepcopy(next(x for x in self.v["observations"]
                                 if x["measurement"] == "softbank_approx_openai_ownership"))
        row["id"] = "SOFTBANK-STAKED-REVISION-003"
        row["supersedes"] = "SFTBY-2026-10-01-OPENAI-STAKE"
        self.v["observations"].append(row)
        delta = mod.compare(old, self.snapshot())
        self.assertIn("B09", delta["recompute_consumer_sparks"])
        self.assertIn("B04", delta["recompute_consumer_sparks"])
        # Old record remains immutable even after the replacement.
        self.assertIn("valuation:SFTBY-2026-10-01-OPENAI-STAKE",
                      self.snapshot()["record_hashes"])

    def test_source_access_change_does_not_reprice_company(self):
        old = self.snapshot()
        self.r["version"] = "0.1.1"
        src = next(x for x in self.r["sources"] if x["id"] == "massive_treasury")
        src["access"] = "NOT_ENTITLED_VERIFIED"
        delta = mod.compare(old, self.snapshot())
        self.assertIn("B02", delta["recompute_consumer_sparks"])
        self.assertNotIn("B04", delta["recompute_consumer_sparks"])
        self.assertNotIn("B09", delta["recompute_consumer_sparks"])

    def test_policy_change_only_reprioritizes_research(self):
        old = self.snapshot()
        self.p["policy_version"] = "0.1.1"
        weights = self.p["stages"]["pre_prospectus"]["base_weights_pct"]
        weights["capital_funding"] += 1
        weights["revenue_quality"] -= 1
        delta = mod.compare(old, self.snapshot())
        self.assertEqual(delta["recompute_consumer_sparks"], ["B13"])

    def test_policy_change_without_version_is_rejected(self):
        old = self.snapshot()
        x = self.p["stages"]["pre_prospectus"]["base_weights_pct"]
        x["capital_funding"] += 1
        x["revenue_quality"] -= 1
        with self.assertRaisesRegex(ValueError, "policy changed without version"):
            mod.compare(old, self.snapshot())

    def test_provider_change_without_version_is_rejected(self):
        old = self.snapshot()
        self.r["sources"][0]["access"] = "NOT_ENTITLED_VERIFIED"
        with self.assertRaisesRegex(ValueError, "provider registry changed without version"):
            mod.compare(old, self.snapshot())

    def test_existing_evidence_cannot_be_silently_overwritten(self):
        old = self.snapshot()
        self.v["observations"][0]["value"] += 1
        with self.assertRaisesRegex(ValueError, "in-place evidence mutation"):
            mod.compare(old, self.snapshot())

    def test_existing_news_cannot_be_silently_overwritten(self):
        old = self.snapshot()
        self.n["items"][0]["metric_or_event"] += " EDITED"
        with self.assertRaisesRegex(ValueError, "in-place evidence mutation"):
            mod.compare(old, self.snapshot())

    def test_deletion_fails_closed(self):
        old = self.snapshot()
        self.n["items"].pop()
        self.n["research_ids"].pop()
        with self.assertRaisesRegex(ValueError, "append-only input deletion"):
            mod.compare(old, self.snapshot())

    def test_duplicate_and_competing_revisions_fail(self):
        self.v["observations"].append(copy.deepcopy(self.v["observations"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate id"):
            self.snapshot()
        self.v["observations"].pop()
        ancestor = self.v["observations"][0]["id"]
        for i in (1, 2):
            row = copy.deepcopy(self.v["observations"][0])
            row["id"] = "REV-" + str(i)
            row["supersedes"] = ancestor
            self.v["observations"].append(row)
        with self.assertRaisesRegex(ValueError, "competing revisions"):
            self.snapshot()

    def test_unavailable_future_and_bad_source_rejected(self):
        self.v["observations"][0]["available_on"] = "2026-11-01"
        with self.assertRaisesRegex(ValueError, "unavailable or future"):
            self.snapshot()
        self.v["observations"][0]["available_on"] = "2026-10-17"
        self.v["observations"][0]["observation_on"] = "2026-10-17"
        self.v["observations"][0]["source_ids"] = ["UNTRACEABLE"]
        with self.assertRaisesRegex(ValueError, "unknown upstream source"):
            self.snapshot()

    def test_cross_vintage_and_intraday_blocked(self):
        with self.assertRaisesRegex(ValueError, "static date-vintage mismatch"):
            mod.build("2027-01-01", valuation=self.v, news=self.n,
                      policy=self.p, resources=self.r)
        with self.assertRaisesRegex(ValueError, "date-only"):
            mod.build("2026-10-17T12:00:00", valuation=self.v, news=self.n,
                      policy=self.p, resources=self.r)

    def test_no_valuation_or_live_claim(self):
        snap = self.snapshot()
        self.assertEqual(snap["source_state"], "research_only_not_live")
        self.assertTrue(snap["valuation_state"].startswith("unknown_"))
        self.assertEqual(snap["parent_nav_state"], "unavailable")
        self.assertTrue(snap["missing_source_timestamps"])

    def test_revision_cycles_rejected(self):
        anchor = self.v["observations"][0]
        correction = copy.deepcopy(anchor)
        correction["id"] = "CYCLE-CHILD-001"
        correction["supersedes"] = anchor["id"]
        anchor["supersedes"] = correction["id"]
        self.v["observations"].append(correction)
        with self.assertRaisesRegex(ValueError, "revision cycle"):
            self.snapshot()

    def test_missing_class_and_negative_weight_rejected(self):
        self.v["observations"][0].pop("source_class")
        with self.assertRaisesRegex(ValueError, "missing class"):
            self.snapshot()
        self.v = mod.load("valuation-register.json")
        x = self.p["stages"]["pre_prospectus"]["base_weights_pct"]
        x["revenue_quality"] = -1
        x["capital_funding"] += 21
        with self.assertRaisesRegex(ValueError, "weights inconsistent"):
            self.snapshot()



if __name__ == "__main__":
    unittest.main()
