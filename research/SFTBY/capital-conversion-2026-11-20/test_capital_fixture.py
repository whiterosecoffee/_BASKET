"""Offline synthetic checks; run: python -m unittest -v test_capital_fixture.py."""
import unittest
from dataclasses import replace
from decimal import Decimal as D
from capital_fixture import compare, evaluate, example_inputs

class AllocationFixtureTests(unittest.TestCase):
    def test_conservation_without_growth_or_cost(self):
        x = replace(example_inputs(), arm_price_return=D(0),
                    project_equity_return=D(0), annual_debt_rate=D(0),
                    sale_cost_rate=D(0), tax_rate_on_sale=D(0),
                    collateral_trigger_verified=True,
                    project_equity_entitlement_verified=True)
        result = compare(x)
        self.assertEqual(result['hold'].ending_nav, D(250))
        self.assertEqual(result['sell_repay'].ending_nav, D(250))
        self.assertEqual(result['sell_reinvest'].ending_nav, D(250))
        self.assertLess(result['sell_repay'].terminal_ltv,
                        result['hold'].terminal_ltv)

    def test_friction_interest_and_foregone_arm_return(self):
        result = compare(example_inputs())
        self.assertEqual(result['hold'].ending_nav, D('258.4'))
        self.assertEqual(result['sell_repay'].ending_nav, D('255.624'))
        self.assertEqual(result['sell_reinvest'].ending_nav, D('257.76'))
        self.assertEqual(result['sell_reinvest'].nav_delta_vs_hold,
                         D('-0.64'))
        self.assertEqual(result['sell_reinvest'].nav_alpha_per_new_dollar,
                         D('-0.64')/D('17.8'))

    def test_zero_return_reinvest_does_not_create_value(self):
        x = replace(example_inputs(), arm_price_return=D(0),
                    project_equity_return=D(0), annual_debt_rate=D(0),
                    sale_cost_rate=D('0.03'))
        self.assertEqual(compare(x)['sell_reinvest'].nav_delta_vs_hold, D('-2.6'))

    def test_missing_collateral_trigger_flag(self):
        result = compare(example_inputs())
        self.assertIn('secured_collateral_threshold_unknown',
                      result['sell_repay'].flags)

    def test_unverified_project_is_blocked(self):
        result = evaluate(example_inputs(), 'sell_reinvest')
        self.assertEqual(result.qualification, 'blocked')

    def test_group_ltv_policy_breach_blocks(self):
        x = replace(example_inputs(), group_ltv_limit=D('0.01'))
        self.assertEqual(evaluate(x, 'hold').qualification, 'blocked')

    def test_pledged_shares_cannot_be_sold(self):
        x = replace(example_inputs(), sale_amount=D(26))
        with self.assertRaises(ValueError):
            evaluate(x, 'sell_repay')

    def test_negative_cash_blocks(self):
        x = replace(example_inputs(), unrestricted_cash=D(1))
        self.assertIn('negative_parent_cash', evaluate(x, 'hold').flags)

    def test_nan_rejected(self):
        x = replace(example_inputs(), arm_price_return=D('NaN'))
        with self.assertRaises(ValueError):
            evaluate(x, 'hold')

    def test_negative_more_than_one_rejected(self):
        x = replace(example_inputs(), arm_price_return=D('-1.1'))
        with self.assertRaises(ValueError):
            evaluate(x, 'hold')

    def test_double_counted_cash_rejected(self):
        x = replace(example_inputs(), arm_value=D(305))
        with self.assertRaises(ValueError):
            evaluate(x, 'hold')

    def test_source_gates_do_not_upgrade_synthetic_to_verified(self):
        x = replace(example_inputs(), collateral_trigger_verified=True,
                    project_equity_entitlement_verified=True)
        self.assertEqual(evaluate(x, 'sell_reinvest').qualification,
                         'provisional')

if __name__ == '__main__':
    unittest.main()
