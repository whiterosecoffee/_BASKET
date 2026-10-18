"""Offline source registry checks. B01 independent integration/CI still required."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("openai_resource_audit", ROOT / "resource_audit.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ResourceAuditTests(unittest.TestCase):
    def setUp(self):
        self.registry=mod.load("resource-registry.json")
        self.policy=mod.load("ipo2027-policy.json")

    def test_source_registry_well_formed(self):
        summary=mod.validate(self.registry,self.policy)
        self.assertEqual(summary["source_count"],15)
        self.assertEqual(summary["working_tested_sources"],2)
        self.assertIn("massive_public_financials",summary["not_entitled_sources"])

    def test_no_fair_value_from_connected_treasuries(self):
        x=mod.evaluate(self.registry,self.policy,"2026-10-17")
        self.assertIsNone(x["OpenAI_fair_value_usd"])
        self.assertIsNone(x["SFTBY_net_NAV"])
        self.assertIsNone(x["IPO_probability"])
        self.assertFalse(x["is_live_feed"])
        self.assertTrue(all(q["fundamental_measurement_completeness"]=="NOT_ESTABLISHED"
                            for q in x["factors"]))

    def test_regime_increases_financing_research_priority_not_value(self):
        a=mod.evaluate(self.registry,self.policy,"2026-10-17",regime="neutral")
        b=mod.evaluate(self.registry,self.policy,"2026-10-17",regime="credit_stress")
        def weight(x,f):
            return next(q["research_weight_pct"] for q in x["factors"] if q["factor"]==f)
        self.assertGreater(weight(b,"capital_funding"),weight(a,"capital_funding"))
        self.assertTrue(b["regime_is_assumed_not_empirically_proven"])

    def test_reject_fabricated_entitlement(self):
        r=self.registry["sources"][1].copy()
        r["access"]="CONNECTED_TESTED_OK"
        r["verified_today"]="not_api_tested"
        self.registry["sources"][1]=r
        with self.assertRaisesRegex(ValueError,"test evidence"):
            mod.validate(self.registry,self.policy)

    def test_no_undated_future_snapshot(self):
        with self.assertRaisesRegex(ValueError,"dated static"):
            mod.evaluate(self.registry,self.policy,"2027-01-01")

    def test_scenario_stage_not_automatically_promoted(self):
        x=mod.evaluate(self.registry,self.policy,"2026-10-17",stage="bookbuilding")
        self.assertEqual(x["stage_status"],"hypothetical_future_stage_NOT_VERIFIED")


if __name__ == "__main__":
    unittest.main()
