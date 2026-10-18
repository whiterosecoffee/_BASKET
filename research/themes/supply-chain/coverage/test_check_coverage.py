"""Adversarial tests for the B19 research candidate checker."""
import copy
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("checker", Path(__file__).with_name("check_coverage.py"))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

def fixture():
    return {"schema": "basket.b19-underrepresented-coverage@1",
            "candidates": [{"ticker": "AMKR", "status": "research_candidate", "canonical_membership": "not_checked",
                            "financial_metrics": "not_ingested", "priority": "P0", "layer": "packaging",
                            "not_in_b19_working_watchlist": True,
                            "evidence": [{"class": "issuer", "claim": "Example only", "url": "https://example.org/test",
                                          "published_at": "2026-07-23"}]}]}

class CoverageChecks(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(checker.check(fixture(), {"tickers": [{"entity_id": "NVDA"}]})["combined"], 2)
    def test_duplicate(self):
        doc = fixture(); doc["candidates"].append(copy.deepcopy(doc["candidates"][0]))
        with self.assertRaises(checker.CoverageError): checker.check(doc)
    def test_overlap(self):
        with self.assertRaises(checker.CoverageError):
            checker.check(fixture(), {"tickers": [{"entity_id": "AMKR"}]})
    def test_promoted_without_authority(self):
        doc = fixture(); doc["candidates"][0]["canonical_membership"] = "verified"
        with self.assertRaises(checker.CoverageError): checker.check(doc)
    def test_financial_claim(self):
        doc = fixture(); doc["candidates"][0]["financial_metrics"] = {"revenue_usd": 100}
        with self.assertRaises(checker.CoverageError): checker.check(doc)
    def test_source_url(self):
        doc = fixture(); doc["candidates"][0]["evidence"][0]["url"] = "not-a-url"
        with self.assertRaises(checker.CoverageError): checker.check(doc)
    def test_future_source_not_inferred(self):
        doc = fixture(); doc["candidates"][0]["evidence"][0]["published_at"] = "tomorrow"
        with self.assertRaises(checker.CoverageError): checker.check(doc)
    def test_unsourced_live_price(self):
        doc = fixture(); doc["candidates"][0]["live_price"] = 1
        with self.assertRaises(checker.CoverageError): checker.check(doc)
    def test_bad_priority(self):
        doc = fixture(); doc["candidates"][0]["priority"] = "P9"
        with self.assertRaises(checker.CoverageError): checker.check(doc)

if __name__ == "__main__":
    unittest.main()
