import unittest
from upside import project_case, rank_candidates, break_even_earnings_change

class UpsideTests(unittest.TestCase):
    def test_compounding_and_decomposition(self):
        x=project_case("0.5","-0.4")
        self.assertEqual(x["gross_price_return"],"-0.10")
        self.assertEqual(x["interaction"],"-0.20")
    def test_costs_reduce_returns(self):
        self.assertEqual(project_case("0","0","0.01","0.01")["net_price_return"],"-0.0199")
    def test_break_even_multiple_compression(self):
        self.assertEqual(break_even_earnings_change("-0.2"),"0.25")
    def test_scenario_consistent_rank(self):
        scenarios={"stress":{"A":{"earnings_change":"-0.3","multiple_change":"-0.5"},"B":{"earnings_change":"0","multiple_change":"-0.1"}},
                   "expansion":{"A":{"earnings_change":"0.8","multiple_change":"0.3"},"B":{"earnings_change":"0.2","multiple_change":"0"}}}
        cs=[{"name":"A-heavy","weights":{"A":"0.5","B":"0.5"}},{"name":"B-heavy","weights":{"A":"0.1","B":"0.9"}}]
        out=rank_candidates(cs,scenarios,max_single_weight="0.9",min_stress_return="-0.3")
        self.assertEqual(out[0]["name"],"B-heavy")
        self.assertFalse(out[1]["eligible"])
        self.assertTrue(out[0]["eligible"])
    def test_missing_evidence_rejected(self):
        with self.assertRaises(ValueError):
            rank_candidates([{"name":"a","weights":{"AAA":"1"}}],{"stress":{},"expansion":{}},max_single_weight="1")
    def test_concentration_rejected(self):
        with self.assertRaises(ValueError):
            rank_candidates([{"name":"a","weights":{"AAA":"1"}}],{"stress":{},"expansion":{}},max_single_weight="0.5")
    def test_no_probabilities(self):
        self.assertNotIn("probability",project_case("0","0"))

if __name__=="__main__":
    unittest.main()
