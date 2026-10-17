"""Narrative engine replay / non-lookahead / stale-quote controls."""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("basket_narrative", ROOT / "engines/narrative/engine.py")
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
CASE = ROOT / "engines/narrative/cases/coreweave_2026-10-16.jsonl"


class NarrativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = engine.load(CASE)
        cls.at = engine.when("2026-10-16T15:00:00Z")

    def test_primary_sec_fact_has_surviving_ttd(self):
        record = next(r for r in self.rows if r["id"] == "crwv-rpo-q2")
        self.assertEqual(engine.freshness(record, self.at), "alive")

    def test_article_quote_has_died(self):
        record = next(r for r in self.rows if r["id"] == "oai-perp-val-oct16")
        self.assertEqual(engine.freshness(record, self.at), "dead")

    def test_no_lookahead(self):
        record = next(r for r in self.rows if r["id"] == "crwv-rpo-q2")
        self.assertEqual(engine.freshness(record, engine.when("2026-08-11T00:00:00Z")),
                         "not_yet_available")

    def test_rpo_derivation(self):
        result = engine.extrapolate(self.rows, self.at)
        d = {x["metric"]: x for x in result["derived"]}
        self.assertAlmostEqual(d["rpo_0_24_usd_b"]["value"], 42.517, places=3)
        self.assertAlmostEqual(d["rpo_25_48_usd_b"]["value"], 40.443, places=3)
        self.assertAlmostEqual(d["rpo_49_78_usd_b"]["value"], 20.74, places=3)
        self.assertAlmostEqual(d["rpo_0_24_annualized_usd_b"]["value"], 21.2585, places=3)
        self.assertEqual(set(d["rpo_0_24_usd_b"]["inputs"]),
                         {"crwv-rpo-q2", "crwv-rpo-frac0", "crwv-rpo-frac1"})

    def test_liquidity_not_cash(self):
        d = {x["metric"]: x for x in engine.extrapolate(self.rows, self.at)["derived"]}
        self.assertAlmostEqual(d["reported_liquidity_excluding_undrawn_usd_b"]["value"],
                               5.539, places=3)

    def test_hypothesis_appears_unresolved_and_unsupported(self):
        d = {x["id"]: x for x in engine.audit(self.rows, self.at)["records"]}
        flags = d["h1-crwv-oai-causality"]["flags"]
        self.assertIn("CAUSAL_OR_FORWARD_HYPOTHESIS", flags)
        self.assertIn("MISSING_OR_EXPIRED_EVIDENCE", flags)
        self.assertIn("CORRELATION_NOT_CAUSATION", flags)

    def test_never_extrapolate_stale_q2_figures(self):
        out = engine.extrapolate(self.rows, engine.when("2027-01-01T00:00:00Z"))
        metrics = [x["metric"] for x in out["derived"]]
        self.assertNotIn("rpo_0_24_usd_b", metrics)


    def test_sftby_sensitivity_is_illustrative_not_nav(self):
        d = engine.sensitivity(self.rows, self.at, 1500, -4)
        self.assertEqual(d["classification"], "conditional_sensitivity_not_NAV")
        self.assertAlmostEqual(d["gross_stake_value_usd_b"], 195.0)
        self.assertAlmostEqual(d["gross_stake_change_usd_b"], -7.8)
        with self.assertRaises(ValueError):
            engine.sensitivity(self.rows, self.at, 0, -4)


if __name__ == "__main__":
    unittest.main()
