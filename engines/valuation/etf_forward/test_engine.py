import copy
import unittest
from engine import analyze, sensitivity

BASE = {
    "as_of": "2026-10-30T20:00:00Z",
    "holdings_available_at": "2026-10-29T20:00:00Z",
    "source_manifest": [{"id": "synthetic-test-only", "sha256": "not-external-evidence"}],
    "fixture_kind": "synthetic_test_not_market_data",
    "holdings": [
        {"ticker": "AAA", "weight": "0.6", "market_cap_usd": "100",
         "market_cap_currency": "USD", "estimates": {
             "2027": {"calendar_year": 2027, "net_income_usd": "10", "currency": "USD", "available_at": "2026-10-29T20:00:00Z"},
             "2028": {"calendar_year": 2028, "net_income_usd": "12", "currency": "USD", "available_at": "2026-10-29T20:00:00Z"}}},
        {"ticker": "BBB", "weight": "0.4", "market_cap_usd": "100",
         "market_cap_currency": "USD", "estimates": {
             "2027": {"calendar_year": 2027, "net_income_usd": "5", "currency": "USD", "available_at": "2026-10-29T20:00:00Z"},
             "2028": {"calendar_year": 2028, "net_income_usd": "6", "currency": "USD", "available_at": "2026-10-29T20:00:00Z"}}}
    ]
}

class ForwardTests(unittest.TestCase):
    def test_weighted_yield_and_pe(self):
        x = analyze(BASE)
        self.assertEqual(x["years"]["2027"]["earnings_yield"], "0.08")
        self.assertEqual(x["years"]["2027"]["pe"], "12.5")
        self.assertEqual(x["years"]["2028"]["earnings_yield"], "0.096")
    def test_missing_coverage_no_pe(self):
        x = copy.deepcopy(BASE)
        del x["holdings"][1]["estimates"]["2027"]
        y = analyze(x)["years"]["2027"]
        self.assertEqual(y["coverage_weight"], "0.6")
        self.assertIsNone(y["pe"])
    def test_negative_earnings_not_averaged(self):
        x = copy.deepcopy(BASE)
        x["holdings"][1]["estimates"]["2027"]["net_income_usd"] = "-20"
        self.assertIsNone(analyze(x)["years"]["2027"]["pe"])
    def test_lookahead_rejected(self):
        x = copy.deepcopy(BASE)
        x["holdings"][0]["estimates"]["2027"]["available_at"] = "2026-11-01T00:00:00Z"
        with self.assertRaises(ValueError):
            analyze(x)
    def test_weights_and_currency_rejected(self):
        x = copy.deepcopy(BASE)
        x["holdings"][0]["weight"] = "0.7"
        with self.assertRaises(ValueError):
            analyze(x)
        x = copy.deepcopy(BASE)
        x["holdings"][0]["estimates"]["2027"]["currency"] = "JPY"
        with self.assertRaises(ValueError):
            analyze(x)
    def test_decomposition(self):
        s = sensitivity(".08", [".2"], [".8"])[0]
        self.assertEqual(s["price_return_ex_distributions"], "-0.04")
        self.assertEqual(s["interaction"], "-0.04")
    def test_reproducible_hash(self):
        self.assertEqual(analyze(BASE)["input_sha256"], analyze(copy.deepcopy(BASE))["input_sha256"])

if __name__ == "__main__":
    unittest.main()
