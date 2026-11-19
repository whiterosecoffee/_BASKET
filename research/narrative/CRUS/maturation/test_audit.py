"""Synthetic adversarial fixtures; no financial observations are fabricated."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from audit import REQUIRED, audit

AT = "2026-11-04T23:33:21Z"


def fixture():
    records = []
    for metric in REQUIRED:
        r = {"id": metric, "metric": metric, "kind": "issuer_statement",
             "review": "source_read", "value": 1, "basis": "current",
             "source": {"url": "https://example.com/SYNTHETIC", "class": "primary"},
             "available_at": "2026-11-04T20:00:00Z", "observed_at": "2026-11-04T21:00:00Z",
             "ingested_at": "2026-11-04T22:00:00Z", "valid_until": "2026-11-05T00:00:00Z"}
        if metric.startswith("eps_"):
            r.update(fiscal_year=int(metric[-4:]), accounting_basis="GAAP", currency="USD", basis="estimate")
        if metric == "quote":
            r.update(currency="USD", venue="NASDAQ", session="regular")
        if metric == "capital_structure":
            r.update(currency="USD", value={"cash_usd":10,"debt_usd":0,"diluted_shares":1})
        records.append(r)
    return {"contract": "crus-research-snapshot@1", "ticker": "CRUS", "records": records, "hypotheses": []}


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.data = fixture()

    def test_complete_synthetic_inputs_do_not_generate_valuation(self):
        r = audit(self.data, AT)
        self.assertEqual(r["status"], "inputs_eligible_for_owner_review")
        self.assertIsNone(r["valuation"])
        self.assertIsNone(r["investment_score"])

    def test_repeat_is_identical_and_input_unchanged(self):
        before = copy.deepcopy(self.data)
        self.assertEqual(audit(self.data, AT), audit(self.data, AT))
        self.assertEqual(before, self.data)

    def test_digest_changes_on_evidence_change(self):
        old = audit(self.data, AT)["input_sha256"]
        self.data["records"][0]["value"] = 2
        self.assertNotEqual(old, audit(self.data, AT)["input_sha256"])

    def test_missing_required_metric_blocks(self):
        self.data["records"].pop()
        self.assertEqual(audit(self.data, AT)["status"], "blocked")

    def test_unknown_never_becomes_zero(self):
        r = self.data["records"][0]
        r.update(kind="unknown", value=None, review="pending")
        self.assertEqual(audit(self.data, AT)["status"], "blocked")
        r["value"] = 0
        with self.assertRaises(ValueError): audit(self.data, AT)

    def test_each_future_timestamp_blocks(self):
        for key in ("available_at", "observed_at", "ingested_at"):
            with self.subTest(key=key):
                d = copy.deepcopy(self.data)
                d["records"][0][key] = "2026-11-04T23:59:00Z"
                if key in {"observed_at", "available_at"}: d["records"][0]["ingested_at"] = "2026-11-04T23:59:01Z"
                self.assertEqual(audit(d, AT)["status"], "blocked")

    def test_null_timestamp_blocks(self):
        self.data["records"][0]["available_at"] = None
        self.assertEqual(audit(self.data, AT)["status"], "blocked")

    def test_expiry_boundary_blocks(self):
        self.data["records"][0]["valid_until"] = AT
        self.assertEqual(audit(self.data, AT)["status"], "blocked")

    def test_historical_input_cannot_be_current(self):
        self.data["records"][0]["basis"] = "historical"
        self.assertEqual(audit(self.data, AT)["status"], "blocked")

    def test_conflict_blocks(self):
        self.data["records"][0]["review"] = "conflicted"
        self.assertEqual(audit(self.data, AT)["status"], "blocked")

    def test_duplicate_id_rejected(self):
        self.data["records"].append(copy.deepcopy(self.data["records"][0]))
        with self.assertRaises(ValueError): audit(self.data, AT)

    def test_duplicate_metric_not_silently_selected(self):
        r = copy.deepcopy(self.data["records"][0]); r["id"] = "second"
        self.data["records"].append(r)
        self.assertEqual(audit(self.data, AT)["status"], "blocked")

    def test_nonfinite_rejected(self):
        for value in (float("nan"), float("inf")):
            self.data["records"][0]["value"] = value
            with self.assertRaises(ValueError): audit(self.data, AT)

    def test_eps_period_basis_currency_rejected(self):
        for key, value in (("fiscal_year",2028),("accounting_basis","mixed"),("currency","JPY"),("value",True)):
            d = copy.deepcopy(self.data)
            d["records"][4][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): audit(d, AT)

    def test_hypothesis_requires_falsifier(self):
        self.data["hypotheses"] = [{"dependencies":["product_role"]}]
        with self.assertRaises(ValueError): audit(self.data, AT)

    def test_unknown_dependency_rejected(self):
        self.data["hypotheses"] = [{"dependencies":["missing"], "alternatives":["a"], "falsifiers":["f"], "milestone":"m"}]
        with self.assertRaises(ValueError): audit(self.data, AT)

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError): audit(self.data, "2026-11-04T23:00:00")

    def test_real_snapshot_blocks_valuation(self):
        p = Path(__file__).with_name("snapshot-2026-11-04.json")
        self.assertEqual(audit(json.loads(p.read_text()), AT)["status"], "blocked")

    def test_cli_blocked_exit_is_not_success(self):
        root = Path(__file__).parent
        r = subprocess.run([sys.executable,str(root/"audit.py"),str(root/"snapshot-2026-11-04.json"),"--as-of",AT],capture_output=True,text=True)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(json.loads(r.stdout)["status"], "blocked")

    def test_malformed_nested_input_is_rejected(self):
        with self.assertRaises(ValueError): audit([], AT)
        for value in (None, 123, []):
            d = copy.deepcopy(self.data); d["records"][0]["source"]["url"] = value
            with self.subTest(value=value), self.assertRaises(ValueError): audit(d, AT)
        self.data["hypotheses"] = [None]
        with self.assertRaises(ValueError): audit(self.data, AT)

    def test_ingestion_cannot_precede_availability(self):
        self.data["records"][0]["available_at"] = "2026-11-04T23:00:00Z"
        with self.assertRaises(ValueError): audit(self.data, AT)

    def test_known_null_is_rejected(self):
        self.data["records"][0]["value"] = None
        with self.assertRaises(ValueError): audit(self.data, AT)

    def test_quote_must_be_positive_usd_and_session_identified(self):
        for field,value in (("value",-1),("value",True),("currency","JPY"),("session","unknown"),("venue","")):
            d=copy.deepcopy(self.data); d["records"][6][field]=value
            with self.subTest(field=field,value=value), self.assertRaises(ValueError): audit(d,AT)

    def test_concentration_must_be_fraction(self):
        self.data["records"][2]["value"]=90
        with self.assertRaises(ValueError): audit(self.data,AT)

    def test_capital_structure_cannot_be_placeholder(self):
        self.data["records"][7]["value"]=1
        with self.assertRaises(ValueError): audit(self.data,AT)

    def test_hypothesis_string_is_not_falsifier_list(self):
        self.data["hypotheses"]=[{"dependencies":["product_role"],"alternatives":"a","falsifiers":"f","milestone":"m"}]
        with self.assertRaises(ValueError): audit(self.data,AT)

    def test_https_prefix_without_host_rejected(self):
        self.data["records"][0]["source"]["url"]="https://"
        with self.assertRaises(ValueError): audit(self.data,AT)


if __name__ == "__main__": unittest.main()
