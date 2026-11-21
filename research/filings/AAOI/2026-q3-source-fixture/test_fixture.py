"""Negative acceptance checks for the AAOI two-source research fixture.

Research-only: does not fetch sources or write accepted canonical ticker events.
Run: python -m unittest discover -s research/filings/AAOI/2026-q3-source-fixture -p 'test_*.py' -v
"""
import json
import unittest
from pathlib import Path

FIXTURE = json.loads((Path(__file__).parent / "fixture.json").read_text(encoding="utf-8"))


class AAOIFixtureContractTests(unittest.TestCase):
    def test_one_economic_event_multiple_official_documents(self):
        event = FIXTURE["canonical_candidate"]
        sources = FIXTURE["source_documents"]
        self.assertEqual(len(sources), 2)
        self.assertEqual(len(set(s["id"] for s in sources)), 2)
        self.assertEqual(len(set(event["source_ids"])), 2)
        self.assertEqual(set(event["source_ids"]), {s["id"] for s in sources})
        self.assertEqual(event["id"], FIXTURE["economic_event_id"])
        self.assertEqual(event["type"], "earnings")
        self.assertEqual(event["reported_period_end"], FIXTURE["period_end"])

    def test_reported_revenue_units_and_guidance_separation(self):
        metrics = {x["metric"]: x for x in FIXTURE["canonical_candidate"]["reported_values"]}
        self.assertEqual(metrics["revenue"]["value"], 269875000)
        self.assertEqual(metrics["prior_year_revenue"]["value"], 118630000)
        self.assertTrue(all(x["unit"] == "USD" for x in metrics.values()))
        guidance = FIXTURE["separate_forward_guidance"]
        self.assertEqual(guidance["status"], "issuer_forecast_not_observed")
        self.assertEqual(guidance["revenue_range_usd"], [385000000, 420000000])
        self.assertNotIn("guidance_revenue", metrics)

    def test_unverified_raw_capture_never_claims_persistence(self):
        validation = FIXTURE["verification"]
        self.assertFalse(validation["full_raw_bytes_saved"])
        self.assertFalse(validation["acceptance_timestamp_verified"])
        self.assertFalse(validation["canonical_persistence_verified"])
        self.assertTrue(validation["historical_backfill"])
        self.assertFalse(validation["alert_allowed"])
        self.assertFalse(FIXTURE["canonical_candidate"]["accepted"])
        self.assertFalse(FIXTURE["canonical_candidate"]["notification_candidate"])
        for source in FIXTURE["source_documents"]:
            self.assertIsNone(source["raw_document_sha256"])
            self.assertIsNone(source["available_at"])
            self.assertTrue(source["url"].startswith("https://"))

    def test_time_guard_unknown_availability_is_not_historical_proof(self):
        self.assertIn("unknown", FIXTURE["verification"]["as_of_rule"])
        self.assertIsNone(FIXTURE["canonical_candidate"]["ingested_at"])

    def test_no_duplicate_period_metrics_from_ir(self):
        values = FIXTURE["canonical_candidate"]["reported_values"]
        self.assertEqual(sum(v["metric"] == "revenue" for v in values), 1)
        self.assertEqual(sum(v["metric"] == "prior_year_revenue" for v in values), 1)


if __name__ == "__main__":
    unittest.main()
