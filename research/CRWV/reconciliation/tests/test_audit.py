import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("crwv_audit", ROOT / "audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
DATA = json.loads((ROOT / "evidence/snapshot.json").read_text())


class AuditTests(unittest.TestCase):
    def test_filed_earnings_bridge_and_sbc(self):
        r = audit.earnings_bridge(DATA["earnings"])
        self.assertEqual(r["gaap_net_income_m"], -709)
        self.assertEqual(r["adjusted_net_income_m"], -529)
        self.assertEqual(r["adjustment_total_m"], 180)
        self.assertAlmostEqual(r["gaap_eps_calculated"], -1.2683363148)

    def test_debt_principal_leases_restricted_cash(self):
        r = audit.balance_bridge(DATA["balance"])
        self.assertEqual(r["debt_carrying_m"], 46873)
        self.assertEqual(r["debt_principal_m"], 47505)
        self.assertEqual(r["net_debt_with_finance_leases_m"], 43338)
        self.assertEqual(r["restricted_cash_excluded_m"], 2282)

    def test_cash_conservation_and_prepaid_revenue(self):
        r = audit.cash_bridge(DATA["cash"])
        self.assertEqual(r["closing_total_cash_m"], 6404)
        self.assertEqual(r["operating_cash_less_cash_ppe_purchases_m"], -7466)
        self.assertEqual(r["operating_cash_excluding_deferred_revenue_change_m"], -152)

    def test_conflicting_eps_never_becomes_verified_pe(self):
        r = audit.evaluate(DATA, DATA["as_of"])
        self.assertTrue(all(x["verified_gaap_pe"] is None for x in r["forward_estimates"]))
        self.assertAlmostEqual(r["forward_estimates"][1]["diagnostic_price_over_reported_eps"], 26.16556, places=4)
        self.assertEqual(r["forward_estimates"][3]["unexplained_pretax_residual_m"], -2296.6)

    def test_gaap_same_basis_reconciliation_is_accepted(self):
        row = {"source_id": "synthetic", "fiscal_year": 2028, "eps": 2, "basis": "gaap", "net_income_m": 1200, "diluted_shares_m": 600}
        r = audit.forward_audit(row, 40, "2026-11-20T22:00:00Z", {"available_at": "2026-11-20T21:00:00Z"})
        self.assertEqual(r["verified_gaap_pe"], 20)
        row["diluted_shares_m"] = 700
        self.assertIsNone(audit.forward_audit(row,40,"2026-11-20T22:00:00Z",{"available_at":"2026-11-20T21:00:00Z"})["verified_gaap_pe"])

    def test_future_information_is_blocked_and_input_unchanged(self):
        before = copy.deepcopy(DATA)
        r = audit.evaluate(DATA, "2026-11-20T22:00:00Z")
        self.assertEqual(r["earnings"]["status"], "future")
        self.assertIsNone(r["historical_balance_ev_reference_m"])
        self.assertEqual(DATA,before)

    def test_missing_and_nonfinite_inputs_raise(self):
        for value in (None, True, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit.number(value)
        b = copy.deepcopy(DATA["balance"])
        b["unamortized_discount_and_costs_m"] = 0
        with self.assertRaises(ValueError):
            audit.balance_bridge(b)

    def test_expected_deposits_do_not_establish_funding(self):
        r = audit.funding_readiness(DATA["funding"])
        self.assertIsNone(r["fully_funded"])
        self.assertIsNone(r["funding_gap_m"])
        self.assertEqual(len(r["missing"]), 6)

    def test_future_forward_values_are_redacted(self):
        row = DATA["forward_estimates"][1]
        r = audit.forward_audit(row,40,"2026-11-20T22:00:00Z",{"available_at":"2026-11-21T00:00:00Z"})
        self.assertEqual(r["status"], "future")
        self.assertIsNone(r["reported_eps"])
        self.assertIsNone(r["diagnostic_price_over_reported_eps"])

    def test_replay_determinism_and_strict_timestamp(self):
        self.assertEqual(audit.evaluate(DATA, DATA["as_of"]), audit.evaluate(DATA, DATA["as_of"]))
        with self.assertRaises(ValueError):
            audit.instant("2026-11-20T22:00:00")


if __name__ == "__main__":
    unittest.main()
