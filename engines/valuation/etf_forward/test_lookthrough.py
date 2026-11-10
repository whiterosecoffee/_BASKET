import copy
import unittest
from lookthrough import calculate

T = "2026-10-30T20:00:00Z"
EST = "2026-10-29T20:00:00Z"
BASE = {
 "as_of": T, "data_kind": "synthetic_test", "source_manifest": [{"id": "toy-only"}],
 "holdings_available_at": EST, "holdings": [
  {"id":"A", "asset_type":"equity", "available_at":EST, "weight":"0.5", "equity_currency":"USD", "market_cap_usd":"100", "estimates": {
   "2027":{"calendar_year":2027,"available_at":EST,"currency":"USD","net_income_usd":"10"},
   "2028":{"calendar_year":2028,"available_at":EST,"currency":"USD","net_income_usd":"15"}}},
  {"id":"B", "asset_type":"equity", "available_at":EST, "weight":"0.4", "equity_currency":"USD", "market_cap_usd":"200", "estimates": {
   "2027":{"calendar_year":2027,"available_at":EST,"currency":"USD","net_income_usd":"-10"},
   "2028":{"calendar_year":2028,"available_at":EST,"currency":"USD","net_income_usd":"20"}}},
  {"id":"CASH", "asset_type":"cash", "currency":"USD", "available_at":EST, "weight":"0.1"}
 ]}

class LookthroughTests(unittest.TestCase):
 def test_cash_and_negative_earnings(self):
  a=calculate(BASE)
  self.assertEqual(a["years"]["2027"]["earnings_yield_known_contribution"],"0.03")
  self.assertEqual(a["years"]["2027"]["equity_coverage_ratio"],"1")
  self.assertEqual(a["years"]["2028"]["earnings_yield_known_contribution"],"0.115")
  self.assertIsNotNone(a["years"]["2027"]["pe"])
 def test_missing_estimate_null_pe(self):
  x=copy.deepcopy(BASE);del x["holdings"][1]["estimates"]["2027"]
  y=calculate(x)["years"]["2027"]
  self.assertIsNone(y["pe"])
  self.assertEqual(y["missing_equity_ids"],["B"])
 def test_nonpositive_yield_null_pe(self):
  x=copy.deepcopy(BASE);x["holdings"][1]["estimates"]["2027"]["net_income_usd"]="-30"
  self.assertIsNone(calculate(x)["years"]["2027"]["pe"])
 def test_future_estimate_rejected(self):
  x=copy.deepcopy(BASE);x["holdings"][0]["estimates"]["2027"]["available_at"]="2026-11-01T00:00:00Z"
  with self.assertRaises(ValueError):calculate(x)
 def test_duplicate_rejected(self):
  x=copy.deepcopy(BASE);x["holdings"][1]["id"]="A"
  with self.assertRaises(ValueError):calculate(x)
 def test_derivative_rejected(self):
  x=copy.deepcopy(BASE);x["holdings"][2]["asset_type"]="derivative"
  with self.assertRaises(ValueError):calculate(x)
 def test_currency_rejected(self):
  x=copy.deepcopy(BASE);x["holdings"][0]["equity_currency"]="EUR"
  with self.assertRaises(ValueError):calculate(x)
 def test_fiscal_mismatch_rejected(self):
  x=copy.deepcopy(BASE);x["holdings"][0]["estimates"]["2028"]["calendar_year"]=2027
  with self.assertRaises(ValueError):calculate(x)
 def test_weight_sum_rejected(self):
  x=copy.deepcopy(BASE);x["holdings"][0]["weight"]="0.4"
  with self.assertRaises(ValueError):calculate(x)
 def test_reproducible(self):
  self.assertEqual(calculate(BASE)["input_sha256"],calculate(copy.deepcopy(BASE))["input_sha256"])
 def test_other_year_missing_independent(self):
  x=copy.deepcopy(BASE);del x["holdings"][1]["estimates"]["2028"]
  y=calculate(x)["years"]
  self.assertIsNotNone(y["2027"]["pe"])
  self.assertIsNone(y["2028"]["pe"])

if __name__ == "__main__": unittest.main()
