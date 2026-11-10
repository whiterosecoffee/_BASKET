"""B13 offline deterministic tests. Execute: python -m unittest research/OPENAI/test_ipo2027.py"""
import importlib.util
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("openai_ipo2027", BASE / "ipo2027.py")
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


class IPO2027Tests(unittest.TestCase):
    def test_stage_policy_sums_and_sources(self):
        p = engine.read("ipo2027-policy.json")
        n = engine.read("ipo2027-news.json")
        results = engine.verify(p, n)
        self.assertEqual(results["stages"], 4)
        self.assertEqual(results["verified_news_records"], 15)

    def test_credit_stress_rotates_financing_weight(self):
        p = engine.read("ipo2027-policy.json")
        normal = engine.weights(p, "pre_prospectus", "neutral")
        stressed = engine.weights(p, "pre_prospectus", "credit_stress")
        self.assertAlmostEqual(sum(stressed.values()), 100, places=7)
        self.assertGreater(stressed["capital_funding"], normal["capital_funding"])
        self.assertLess(stressed["revenue_quality"], normal["revenue_quality"])

    def test_stages_shift_weights_only_on_disclosures(self):
        p = engine.read("ipo2027-policy.json")
        x = engine.weights(p, "pre_prospectus", "neutral")
        y = engine.weights(p, "bookbuilding", "neutral")
        self.assertGreater(y["market_price_discovery"], x["market_price_discovery"])
        with self.assertRaisesRegex(ValueError, "stage blocked"):
            engine.run("2026-10-17", stage="bookbuilding")

    def test_unrated_evidence_is_unknown_not_imputed(self):
        output = engine.run("2026-10-17")
        self.assertIsNone(output["evidence_quality"]["observed_quality_score"])
        self.assertEqual(output["evidence_quality"]["quality_interval"], [0, 100])
        self.assertEqual(output["evidence_quality"]["coverage"], 0)
        self.assertIsNone(output["IPO_probability"])
        self.assertIsNone(output["net_SFTBY_NAV"])

    def test_asof_never_uses_later_research(self):
        out = engine.run("2026-04-15")
        self.assertNotIn("REV-2026-10-08-SEP-50", out["available_evidence_ids"])
        self.assertIn("ENT-2026-04-08-40PCT", out["available_evidence_ids"])
        with self.assertRaisesRegex(ValueError, "future-as-of"):
            engine.run("2027-01-01")

    def test_reliability_requires_source_and_date(self):
        w = engine.weights(engine.read("ipo2027-policy.json"), "pre_prospectus", "neutral")
        evidence = engine.run("2026-10-17")["available_evidence_ids"]
        r = {"revenue_quality": {"score": 72, "reliability": 0.5,
                                 "source_ids": ["REV-2026-10-08-SEP-50"],
                                 "available_on": "2026-10-08"}}
        z = engine.rating_summary(w, r, set(evidence), "2026-10-17")
        self.assertAlmostEqual(z["coverage"], 0.1)
        self.assertEqual(z["observed_quality_score"], 72)
        self.assertEqual(z["quality_interval"], [7.2, 97.2])
        r["revenue_quality"]["source_ids"] = ["NOT_IN_EVIDENCE"]
        with self.assertRaisesRegex(ValueError, "point-in-time"):
            engine.rating_summary(w, r, set(evidence), "2026-10-17")

    def test_sensitivity_exact_and_not_fair_value(self):
        x = engine.scenario(100, 10, 10, 15, 5)
        self.assertEqual(x["implied_EV_usd_b"], 1000)
        self.assertEqual(x["implied_equity_usd_b"], 990)
        self.assertIn("not_fair_value", x["classification"])
        with self.assertRaises(ValueError):
            engine.scenario(100, 10, None, 15, 5)
        with self.assertRaises(ValueError):
            engine.scenario(100, float("nan"), 10, 15, 5)

    def test_regime_is_assumption_not_observed_causality(self):
        result = engine.run("2026-10-17", regime="credit_stress")
        self.assertEqual(result["regime_state"], "conditional_user_selected_regime")


if __name__ == "__main__":
    unittest.main()
