"""Offline adversarial tests for B19 research proposal shape (not source verification)."""
import copy
import importlib.util
import json
import pathlib
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_research", HERE / "check_research.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ROOT = HERE.parent
FILES = ("registry/tickers.json", "coverage/missing.json", "registry/pools.json",
         "earnings/quarterly-intake.json", "relationships/gateway-model.json",
         "reconciliation/rules.json")

class ResearchContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.docs = {}
        for rel in FILES:
            self.docs[rel] = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        self.row = {
            "entity_id": "MSFT", "fiscal_period": "FY2026-Q4", "period_end": "2026-06-30",
            "published_at": "2026-07-29T20:00:00Z", "available_at": "2026-07-29T20:00:00Z",
            "ingested_at": "2026-07-30T00:00:00Z", "source_url": "https://example.com/issuer",
            "metric": "segment_revenue", "value_usd": 1000, "classification": "issuer_reported",
            "revision_id": "fixture-r1"
        }
    def check(self):
        for rel, data in self.docs.items():
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(data), encoding="utf-8")
        return mod.validate(self.root)
    def test_empty_scaffold(self):
        self.assertEqual(self.check(), [])
    def test_populated_proposal(self):
        self.docs["earnings/quarterly-intake.json"]["proposals"].append(copy.deepcopy(self.row))
        self.assertEqual(self.check(), [])
    def test_duplicate_revision(self):
        self.docs["earnings/quarterly-intake.json"]["proposals"] = [self.row, copy.deepcopy(self.row)]
        self.assertTrue(any("duplicate revision" in e for e in self.check()))
    def test_missing_source(self):
        self.row["source_url"] = ""
        self.docs["earnings/quarterly-intake.json"]["proposals"] = [self.row]
        self.assertTrue(any("evidence URL" in e for e in self.check()))
    def test_lookahead(self):
        self.row["available_at"] = "2026-07-28T00:00:00Z"
        self.docs["earnings/quarterly-intake.json"]["proposals"] = [self.row]
        self.assertTrue(any("chronology" in e for e in self.check()))
    def test_unknown_entity(self):
        self.row["entity_id"] = "NOT_IN_RESEARCH"
        self.docs["earnings/quarterly-intake.json"]["proposals"] = [self.row]
        self.assertTrue(any("outside research" in e for e in self.check()))
    def test_research_not_canonical(self):
        self.docs["registry/tickers.json"]["authority"] = "canonical"
        self.assertTrue(any("canonical entity" in e for e in self.check()))
    def test_unmeasured_pool_claim(self):
        self.docs["registry/pools.json"]["pools"][0]["quarterly_final_demand_usd"] = 500
        self.assertTrue(any("unmeasured" in e for e in self.check()))
    def test_gateway_hypothesis(self):
        self.docs["relationships/gateway-model.json"]["hypotheses"].append({
            "source_entity_id": "MSFT", "target_entity_id": "CRWV",
            "relationship_type": "procurement_hypothesis", "classification": "hypothesis",
            "source_url": "https://example.com/claim", "available_at": "2026-07-29T20:00:00Z",
            "revision_id": "fixture-edge-1"
        })
        self.assertEqual(self.check(), [])
    def test_gateway_unsourced_money(self):
        self.docs["relationships/gateway-model.json"]["hypotheses"].append({
            "source_entity_id": "MSFT", "target_entity_id": "CRWV",
            "relationship_type": "procurement_hypothesis", "classification": "hypothesis",
            "source_url": "https://example.com/claim", "available_at": "2026-07-29T20:00:00Z",
            "revision_id": "fixture-edge-1", "flow_usd": 999
        })
        self.assertTrue(any("monetary flow" in e for e in self.check()))

if __name__ == "__main__":
    unittest.main()
