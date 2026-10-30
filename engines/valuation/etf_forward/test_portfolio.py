import copy,unittest
from decimal import Decimal
from portfolio import compare
T="2026-10-29T20:00:00Z"
BASE={"as_of":"2026-10-30T20:00:00Z","data_kind":"synthetic_test",
 "source_manifest":[{"id":"toy-synthetic"}],
 "securities":[{"id":s,"currency":"USD","available_at":T} for s in ("NVDA","TSM","AVGO","KLAC")],
 "portfolios":[
 {"name":"Mock ETF","holdings_available_at":T,"weights":{"NVDA":".25","TSM":".25","AVGO":".25","KLAC":".25"},"holding_period_fees":".01"},
 {"name":"Mock custom","holdings_available_at":T,"weights":{"NVDA":".5","TSM":".2","AVGO":".2","KLAC":".1"},"round_trip_cost":".01"}],
 "scenarios":{name:{"available_at":T,"constituents":{
 s:{"available_at":T,"earnings_change":e,"multiple_change":m} for s in ("NVDA","TSM","AVGO","KLAC")}}
 for name,e,m in (("stress","-.2","-.3"),("base",".3","0"),("expansion",".7",".2"))}}
class Tests(unittest.TestCase):
 def test_reproduce(self):
  self.assertEqual(compare(BASE)["sha256"],compare(copy.deepcopy(BASE))["sha256"])
 def test_count(self):
  self.assertEqual(len(compare(BASE)["portfolios"]),2)
 def test_stress(self):
  self.assertEqual(Decimal(compare(BASE)["portfolios"][0]["scenario_returns"]["stress"]),Decimal("-.4456"))
 def test_attribution(self):
  x=copy.deepcopy(BASE)
  x["portfolios"][0]["holding_period_fees"]="0"
  x["portfolios"][1]["round_trip_cost"]="0"
  for p in compare(x)["portfolios"]:
   for name,v in p["scenario_returns"].items():
    self.assertEqual(sum(map(Decimal,p["contributions"][name].values())),Decimal(v))
 def test_holdings_lookahead(self):
  x=copy.deepcopy(BASE);x["portfolios"][0]["holdings_available_at"]="2026-11-01T00:00:00Z"
  with self.assertRaises(ValueError):compare(x)
 def test_estimate_lookahead(self):
  x=copy.deepcopy(BASE);x["scenarios"]["base"]["constituents"]["NVDA"]["available_at"]="2026-11-01T00:00:00Z"
  with self.assertRaises(ValueError):compare(x)
 def test_missing(self):
  x=copy.deepcopy(BASE);del x["scenarios"]["stress"]["constituents"]["KLAC"]
  with self.assertRaises(ValueError):compare(x)
 def test_fx_rejected(self):
  x=copy.deepcopy(BASE);x["securities"][0]["currency"]="JPY"
  with self.assertRaises(ValueError):compare(x)
 def test_weights_rejected(self):
  x=copy.deepcopy(BASE);x["portfolios"][0]["weights"]["TSM"]=".5"
  with self.assertRaises(ValueError):compare(x)
 def test_no_probability(self):
  self.assertNotIn("probability",str(compare(BASE)))
if __name__=="__main__":unittest.main()
