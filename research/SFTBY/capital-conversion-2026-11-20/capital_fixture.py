"""Synthetic holding-company allocation comparisons (USD billions).

Research fixture, not a live SFTBY NAV, investment recommendation, or
authorized trade. Same dated assumptions are used for every action.
"""
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Optional
import json

D = lambda value: Decimal(str(value))

@dataclass(frozen=True)
class Inputs:
    assets: Decimal
    debt: Decimal
    unrestricted_cash: Decimal
    arm_value: Decimal
    arm_unpledged_sale_limit: Decimal
    sale_amount: Decimal
    arm_price_return: Decimal
    project_equity_return: Decimal
    annual_debt_rate: Decimal
    sale_cost_rate: Decimal = D('0')
    tax_rate_on_sale: Decimal = D('0')
    taxable_gain_fraction: Decimal = D('0')
    group_ltv_limit: Decimal = D('0.25')
    collateral_trigger_verified: bool = False
    project_equity_entitlement_verified: bool = False

@dataclass(frozen=True)
class Result:
    action: str
    starting_nav: Decimal
    ending_nav: Decimal
    ending_debt: Decimal
    ending_unrestricted_cash: Decimal
    ending_arm_value: Decimal
    ending_project_value: Decimal
    financing_cost: Decimal
    sale_friction: Decimal
    terminal_ltv: Decimal
    nav_delta_vs_hold: Optional[Decimal]
    nav_alpha_per_new_dollar: Optional[Decimal]
    qualification: str
    flags: tuple[str, ...]

def evaluate(x: Inputs, action: str) -> Result:
    if action not in {'hold', 'sell_repay', 'sell_reinvest'}:
        raise ValueError('unknown action')
    nums = (x.assets, x.debt, x.unrestricted_cash, x.arm_value,
            x.arm_unpledged_sale_limit, x.sale_amount, x.annual_debt_rate)
    if any(not n.is_finite() or n < 0 for n in nums):
        raise ValueError('nonfinite or negative accounting input')
    rates = (x.arm_price_return, x.project_equity_return, x.sale_cost_rate,
             x.tax_rate_on_sale, x.taxable_gain_fraction, x.group_ltv_limit)
    if any(not n.is_finite() for n in rates):
        raise ValueError('nonfinite scenario input')
    if x.arm_price_return < -1 or x.project_equity_return < -1:
        raise ValueError('returns below -100%')
    if any(not 0 <= n <= 1 for n in rates[2:]):
        raise ValueError('rate outside [0,1]')
    if x.arm_value + x.unrestricted_cash > x.assets:
        raise ValueError('arm and cash exceed / double count assets')
    if x.sale_amount > min(x.arm_value, x.arm_unpledged_sale_limit):
        raise ValueError('sale exceeds unpledged capacity')
    if action == 'sell_repay' and x.sale_amount > x.debt:
        raise ValueError('sale exceeds repayable debt')

    sale = x.sale_amount if action != 'hold' else D(0)
    friction = sale * (x.sale_cost_rate +
                       x.tax_rate_on_sale * x.taxable_gain_fraction)
    proceeds = sale - friction
    debt = x.debt - proceeds if action == 'sell_repay' else x.debt
    arm = (x.arm_value - sale) * (1 + x.arm_price_return)
    project = (proceeds * (1 + x.project_equity_return)
               if action == 'sell_reinvest' else D(0))
    interest = debt * x.annual_debt_rate
    cash = x.unrestricted_cash - interest
    # Proceeds are directly applied to repayment/reinvestment. Never add to
    # unrestricted parent cash; neither costs nor proceeds count twice.
    other = x.assets - x.arm_value - x.unrestricted_cash
    ending_assets = other + arm + project + cash
    if ending_assets <= 0:
        raise ValueError('terminal assets not positive')
    nav = ending_assets - debt
    ltv = debt / ending_assets
    flags = []
    if cash < 0:
        flags.append('negative_parent_cash')
    if ltv > x.group_ltv_limit:
        flags.append('group_ltv_policy_breach')
    if not x.collateral_trigger_verified:
        flags.append('secured_collateral_threshold_unknown')
    if action == 'sell_reinvest' and not x.project_equity_entitlement_verified:
        flags.append('project_parent_entitlement_unknown')
    blocked = {'negative_parent_cash', 'group_ltv_policy_breach',
               'project_parent_entitlement_unknown'}
    return Result(action, x.assets - x.debt, nav, debt, cash, arm, project,
                  interest, friction, ltv, None, None,
                  'blocked' if blocked.intersection(flags) else 'provisional',
                  tuple(flags))

def compare(x: Inputs) -> dict[str, Result]:
    baseline = evaluate(x, 'hold')
    output = {}
    for action in ('hold', 'sell_repay', 'sell_reinvest'):
        item = evaluate(x, action)
        delta = item.ending_nav - baseline.ending_nav
        invested = (x.sale_amount - item.sale_friction
                    if action == 'sell_reinvest' else D(0))
        ratio = delta / invested if invested > 0 else None
        output[action] = Result(**{**asdict(item),
                                   'nav_delta_vs_hold': delta,
                                   'nav_alpha_per_new_dollar': ratio})
    return output

def example_inputs() -> Inputs:
    return Inputs(assets=D(320), debt=D(70), unrestricted_cash=D(20),
                  arm_value=D(140), arm_unpledged_sale_limit=D(25),
                  sale_amount=D(20), arm_price_return=D('0.10'),
                  project_equity_return=D('0.20'), annual_debt_rate=D('0.08'),
                  sale_cost_rate=D('0.01'), tax_rate_on_sale=D('0.20'),
                  taxable_gain_fraction=D('0.50'), group_ltv_limit=D('0.35'))

if __name__ == '__main__':
    print(json.dumps({
        action: {field: str(value) if isinstance(value, Decimal) else value
                 for field, value in asdict(result).items()}
        for action, result in compare(example_inputs()).items()
    }, indent=2))
