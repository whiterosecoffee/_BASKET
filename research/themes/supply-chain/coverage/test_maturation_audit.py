"""B19 maturation audit positive and negative cases, using standard-library unittest."""
import copy
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("maturation_audit", Path(__file__).with_name("maturation_audit.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assess, MaturityError = module.assess, module.MaturityError
compare_reports = module.compare_reports

def sample():
    mapping = {
        "schema": "basket.b19-whole-basket-role-map@research1",
        "authoritative_scope": {"count": 2, "head_sha": "a" * 40},
        "pool_reference": {"pool_count": 1, "head_sha": "b" * 40},
        "coverage": {"pool_participant_counts": {"semiconductors": 1}},
        "rows": [
            {"symbol": "NVDA", "instrument_type": "equity_or_depositary_receipt",
             "pool_ids": ["semiconductors"], "contract_edges": [],
             "source_supported_revenue_usd": None, "captured_share": None, "production_capacity": None},
            {"symbol": "QQQ", "instrument_type": "fund_or_etp", "pool_ids": [],
             "contract_edges": [], "source_supported_revenue_usd": None,
             "captured_share": None, "production_capacity": None}
        ]
    }
    pools = {"pools": [{"id": "semiconductors", "status": "unmeasured",
                        "quarterly_final_demand_usd": None, "evidence_refs": []}]}
    return mapping, pools

class MaturationAuditTests(unittest.TestCase):
    def test_base(self):
        a, b = sample()
        out = assess(a, b)
        self.assertEqual(out["scope"]["tracked_instruments"], 2)
        self.assertEqual(out["financial_coverage"]["reported_denominator_pools"], 0)
        self.assertIsNone(out["pool_research_queue"][0]["buyer_dollar_coverage_ratio"])

    def test_repeat_determinism(self):
        a, b = sample()
        self.assertEqual(assess(a, b), assess(copy.deepcopy(a), copy.deepcopy(b)))

    def test_duplicate_symbol(self):
        a, b = sample()
        a["rows"].append(copy.deepcopy(a["rows"][0]))
        a["authoritative_scope"]["count"] = 3
        with self.assertRaises(MaturityError): assess(a, b)

    def test_unknown_pool(self):
        a, b = sample()
        a["rows"][0]["pool_ids"] = ["fictional"]
        with self.assertRaises(MaturityError): assess(a, b)

    def test_duplicate_membership(self):
        a, b = sample()
        a["rows"][0]["pool_ids"].append("semiconductors")
        with self.assertRaises(MaturityError): assess(a, b)

    def test_nonissuer_promotion(self):
        a, b = sample()
        a["rows"][1]["pool_ids"] = ["semiconductors"]
        with self.assertRaises(MaturityError): assess(a, b)

    def test_unverified_revenue_rejected(self):
        a, b = sample()
        a["rows"][0]["source_supported_revenue_usd"] = 900
        with self.assertRaises(MaturityError): assess(a, b)

    def test_contract_promotion_rejected(self):
        a, b = sample()
        a["rows"][0]["contract_edges"] = [{"customer": "MSFT"}]
        with self.assertRaises(MaturityError): assess(a, b)

    def test_stale_aggregate_rejected(self):
        a, b = sample()
        a["coverage"]["pool_participant_counts"]["semiconductors"] = 2
        with self.assertRaises(MaturityError): assess(a, b)

    def test_unsourced_demand_rejected(self):
        a, b = sample()
        b["pools"][0].update({"status": "measured", "quarterly_final_demand_usd": 1})
        with self.assertRaises(MaturityError): assess(a, b)

    def test_denominator_alone_not_share(self):
        a, b = sample()
        b["pools"][0].update({"status": "measured", "quarterly_final_demand_usd": 100,
                              "evidence_refs": ["source:1"]})
        out = assess(a, b)
        self.assertEqual(out["financial_coverage"]["reported_denominator_pools"], 1)
        self.assertIsNone(out["pool_research_queue"][0]["buyer_dollar_coverage_ratio"])

    def test_identical_prior_report_is_noop(self):
        a, b = sample()
        report = assess(a, b)
        delta = compare_reports(report, assess(a, b))
        self.assertFalse(delta["requires_reconciliation"])
        self.assertEqual(delta["changed_pool_ids"], [])

    def test_changed_source_revision_requires_reconciliation(self):
        a, b = sample()
        previous = assess(a, b)
        a["authoritative_scope"]["head_sha"] = "c" * 40
        delta = compare_reports(previous, assess(a, b))
        self.assertTrue(delta["upstream_revision_changed"])
        self.assertTrue(delta["requires_reconciliation"])

    def test_incompatible_previous_fails_closed(self):
        a, b = sample()
        with self.assertRaises(MaturityError):
            compare_reports({"schema": "wrong"}, assess(a, b))

    def test_bad_revision(self):
        a, b = sample()
        a["authoritative_scope"]["head_sha"] = "x"
        with self.assertRaises(MaturityError): assess(a, b)

    def test_duplicate_pool(self):
        a, b = sample()
        b["pools"].append(copy.deepcopy(b["pools"][0]))
        a["pool_reference"]["pool_count"] = 2
        with self.assertRaises(MaturityError): assess(a, b)

    def test_nan_demand_rejected(self):
        a, b = sample()
        b["pools"][0].update({"status": "measured", "quarterly_final_demand_usd": float("nan"),
                              "evidence_refs": ["source:1"]})
        with self.assertRaises(MaturityError): assess(a, b)

if __name__ == "__main__":
    unittest.main()
