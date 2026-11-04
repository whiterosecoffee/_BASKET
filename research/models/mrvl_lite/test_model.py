import copy
import json
import unittest
from pathlib import Path
from model import evaluate, paired_spread, pro_forma, rebound, spread


class ModelTests(unittest.TestCase):
    def test_constant_spread_equal_returns(self):
        self.assertAlmostEqual(spread(100, 400, 4.5), spread(110, 440, 4.5))

    def test_low_touch_not_close(self):
        self.assertAlmostEqual(rebound(159.8, 154.78), 0.032433131, places=8)
        self.assertGreater(rebound(626.75, 598.7), rebound(159.8, 154.78))

    def test_reject_mismatched_pair(self):
        a = {"price": 100, "at": "2026-11-04T16:06:00Z", "session": "regular"}
        b = dict(a, price=400, at="2026-11-04T16:07:00Z")
        with self.assertRaises(ValueError):
            paired_spread(a, b, 4.5)

    def test_reject_mixed_session(self):
        a = {"price": 100, "at": "2026-11-04T16:06:00Z", "session": "regular"}
        with self.assertRaises(ValueError):
            paired_spread(a, dict(a, session="extended"), 4.5)

    def test_direct_share_count_math(self):
        self.assertEqual(pro_forma(5, 20, 100, 10, 4, 0, .2, 0), 5)
        self.assertEqual(pro_forma(5, 20, 100, 10, 4, 175, .2, 0), 6)

    def test_negative_eps_allowed(self):
        self.assertLess(pro_forma(-5, -20, 100, 10, 4, 0, .2, 0), 0)

    def test_invalid_numbers(self):
        for bad in (0, -1, float("nan"), float("inf"), True):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                spread(bad, 10, 4.5)

    def test_real_forecast_is_blocked_and_replayable(self):
        case = json.loads(Path(__file__).with_name("case.json").read_text())
        result = evaluate(case)
        self.assertEqual(result, evaluate(copy.deepcopy(case)))
        self.assertIsNone(result["price"])
        self.assertIn("input_conflicts", result["blockers"])

    def test_admitted_synthetic_case(self):
        case = {key: True for key in ("sources_verified", "standalone_estimates_verified",
                "diluted_shares_verified", "periods_aligned", "deal_terms_verified")}
        case.update(acquirer_period_end="2028-12-31", target_period_end="2028-12-31",
                    basis="adjusted", currency="USD", multiple=20,
                    inputs=dict(acquirer_eps=5, target_eps=20, acquirer_shares=100,
                                target_shares=10, ratio=4, savings=0, tax=.2, costs=0))
        self.assertEqual(evaluate(case)["price"], 100)
        case["target_period_end"] = "2028-06-30"
        with self.assertRaises(ValueError):
            evaluate(case)


if __name__ == "__main__":
    unittest.main()
