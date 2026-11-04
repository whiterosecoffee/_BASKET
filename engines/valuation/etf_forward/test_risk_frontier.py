"""Adversarial offline tests: no observed data or investment forecasts."""
import copy
import unittest
from decimal import Decimal
from risk_frontier import historical_risk, pareto_frontier

ASOF="2026-11-03T23:00:00Z"
def fixture():
    names=["A","B","benchmark"]
    return {"as_of":ASOF,"data_kind":"synthetic_test",
      "source_manifest":[{"id":"unit-test-only"}],
      "weight_policy":"daily_constant_weight",
      "weights":{"A":"0.6","B":"0.4"},
      "returns":{k:[{"session":f"2026-09-{i+1:02d}",
        "available_at":"2026-10-01T20:00:00Z",
        "total_return":str(Decimal(i%5-2)*Decimal(v))}
        for i in range(20)] for k,v in zip(names,("0.01","0.005","0.008"))}}

class RiskTests(unittest.TestCase):
    def test_measured_risk(self):
        x=historical_risk(fixture(),minimum_sessions=20)
        self.assertEqual(x["sessions"],20)
        self.assertEqual(x["data_kind"],"synthetic_test")
        self.assertGreater(float(x["annualized_volatility"]),0)
        self.assertLess(float(x["max_drawdown"]),0)
    def test_repeatable(self):
        self.assertEqual(historical_risk(fixture(),20),historical_risk(copy.deepcopy(fixture()),20))
    def test_missing_session(self):
        x=fixture();x["returns"]["A"].pop()
        with self.assertRaises(ValueError):historical_risk(x,19)
    def test_future_available_rejected(self):
        x=fixture();x["returns"]["A"][0]["available_at"]="2026-12-01T00:00:00Z"
        with self.assertRaises(ValueError):historical_risk(x,20)
    def test_unsupported_weights(self):
        x=fixture();x["weights"]["A"]="0.7"
        with self.assertRaises(ValueError):historical_risk(x,20)
    def test_no_free_buy_and_hold_claim(self):
        x=fixture();x["weight_policy"]="buy_and_hold"
        with self.assertRaises(ValueError):historical_risk(x,20)
    def test_insufficient_history(self):
        with self.assertRaises(ValueError):historical_risk(fixture(),60)
    def test_duplicate_session(self):
        x=fixture();x["returns"]["A"][1]["session"]=x["returns"]["A"][0]["session"]
        with self.assertRaises(ValueError):historical_risk(x,20)
    def test_return_less_than_negative_one(self):
        x=fixture();x["returns"]["A"][0]["total_return"]="-1.01"
        with self.assertRaises(ValueError):historical_risk(x,20)

class FrontierTests(unittest.TestCase):
    def row(self,name,up,loss,drawdown="0.3",cost="0.01",conc="0.5",horizon="2027"):
        return {"name":name,"horizon":horizon,"evidence_status":"synthetic_test",
                "conditional_upside":up,"stress_loss":loss,"drawdown_magnitude":drawdown,
                "round_trip_cost":cost,"concentration":conc}
    def test_dominated_eliminated(self):
        rows=[self.row("a","0.4","0.2"),self.row("b","0.3","0.3")]
        self.assertEqual(pareto_frontier(rows,"2027")["non_dominated"],["a"])
    def test_tradeoff_keeps_both(self):
        rows=[self.row("a","0.5","0.4"),self.row("b","0.3","0.1")]
        self.assertEqual(pareto_frontier(rows,"2027")["non_dominated"],["a","b"])
    def test_horizon_isolated(self):
        with self.assertRaises(ValueError):pareto_frontier([self.row("a","0.2","0.2",horizon="2028")],"2027")
    def test_no_missing_risk_or_probability(self):
        x=self.row("a","0.2","0.2");del x["drawdown_magnitude"]
        with self.assertRaises(KeyError):pareto_frontier([x],"2027")
    def test_duplicate_portfolio_rejected(self):
        rows=[self.row("same","0.2","0.2"),self.row("same","0.4","0.3")]
        with self.assertRaises(ValueError):pareto_frontier(rows,"2027")
    def test_2028_supported(self):
        result=pareto_frontier([self.row("a","0.2","0.1",horizon="2028")],"2028")
        self.assertEqual(result["horizon"],"2028")
    def test_nonnegative_risk_required(self):
        with self.assertRaises(ValueError):pareto_frontier([self.row("a","0.2","-0.1")],"2027")

if __name__=="__main__":
    unittest.main()
