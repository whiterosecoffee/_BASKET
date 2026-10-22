"""Illustrative quarterly CRWV model. USD billions; capacity GW; shares billions.

All forward inputs are analyst assumptions conditional on full utilization after
billing readiness. Not a forecast of individual facilities or a full credit model.
"""
import json
from pathlib import Path

CASES = {
    "slow": dict(weight=.30, ends=[1.95, 2.10, 2.25, 2.40, 2.55, 2.70, 2.85, 3.00],
                 yield_2027=15., yield_2028=15., margin=.60, rate=.090, equipment_cost=30.,
                 issue_price=60., multiple=18.),
    "base": dict(weight=.50, ends=[2.05, 2.30, 2.65, 3.00, 3.25, 3.50, 3.75, 4.00],
                 yield_2027=19., yield_2028=17., margin=.64, rate=.075, equipment_cost=35.,
                 issue_price=100., multiple=24.),
    "bull": dict(weight=.20, ends=[2.15, 2.50, 3.00, 3.60, 3.90, 4.20, 4.50, 4.80],
                 yield_2027=28., yield_2028=20., margin=.66, rate=.065, equipment_cost=40.,
                 issue_price=150., multiple=26.),
}

def model(name, case):
    capacity = 1.85
    legacy_debt = 50.
    loans = []
    shares = .600
    cash = 3.
    records = []
    for i, end in enumerate(case["ends"]):
        year = 2027 + i // 4
        added = end - capacity
        average = (capacity + end) / 2
        incremental_average = average - 1.85
        unit_yield = case[f"yield_{year}"]
        revenue = (19. + incremental_average * unit_yield) / 4
        ebitda_after_sbc = revenue * case["margin"]
        depreciation = (9. + incremental_average * case["equipment_cost"] / case.get("new_equipment_life", 6.)) / 4
        capex = added * case["equipment_cost"]
        borrowing = capex * .8
        legacy_principal = min(2.5, legacy_debt)
        old_new_principal = sum(min(l["original"] / 20, l["balance"]) for l in loans)
        initial_principal = borrowing / 40  # half-quarter first installment
        opening_new_debt = sum(l["balance"] for l in loans)
        average_debt = (legacy_debt - legacy_principal/2 + opening_new_debt
                        - old_new_principal/2 + borrowing/2 - initial_principal/2)
        interest = average_debt * case["rate"] / 4
        pretax = ebitda_after_sbc - depreciation - interest
        tax = max(0., pretax) * .20
        income = pretax - tax
        principal = legacy_principal + old_new_principal + initial_principal
        sbc_expense = revenue * .03
        cash_before_equity = (cash + ebitda_after_sbc + sbc_expense - interest
                              - tax - principal - capex + borrowing)
        equity_raised = max(0., -cash_before_equity)
        cash = max(0., cash_before_equity)
        new_shares = equity_raised / case["issue_price"]
        sbc_shares = sbc_expense / case["issue_price"]
        average_shares = shares + (new_shares + sbc_shares)/2
        shares += new_shares + sbc_shares
        legacy_debt -= legacy_principal
        for loan in loans:
            loan["balance"] -= min(loan["original"] / 20, loan["balance"])
        loans.append(dict(original=borrowing, balance=borrowing-initial_principal))
        debt = legacy_debt + sum(l["balance"] for l in loans)
        assert abs((50. + sum(r["borrowing"] for r in records) + borrowing
                    - sum(r["principal"] for r in records) - principal) - debt) < 1e-8
        assert cash >= 0 and added >= 0 and shares > 0
        records.append(dict(period=f"{year}Q{i%4+1}", end_gw=end, added_gw=added,
                            average_gw=average, revenue=revenue,
                            ebitda_after_sbc=ebitda_after_sbc, depreciation=depreciation,
                            interest=interest, pretax=pretax, tax=tax, net_income=income,
                            capex=capex, borrowing=borrowing, principal=principal,
                            end_debt=debt, cash=cash, equity_raised=equity_raised,
                            sbc_expense=sbc_expense, sbc_shares=sbc_shares,
                            average_shares=average_shares, end_shares=shares))
        capacity = end
    years = {}
    for year in (2027, 2028):
        rows = [r for r in records if r["period"].startswith(str(year))]
        totals = {k:sum(r[k] for r in rows) for k in
                  ("revenue", "ebitda_after_sbc", "depreciation", "interest", "net_income",
                   "capex", "borrowing", "principal", "equity_raised")}
        totals["average_shares"] = sum(r["average_shares"] for r in rows)/4
        totals["eps"] = totals["net_income"]/totals["average_shares"]
        totals["end_debt"] = rows[-1]["end_debt"]
        totals["end_cash"] = rows[-1]["cash"]
        totals["end_shares"] = rows[-1]["end_shares"]
        totals["end_gw"] = rows[-1]["end_gw"]
        years[str(year)] = totals
    terminal = years["2028"]["eps"] * case["multiple"]
    return dict(name=name, assumptions=case, quarters=records, years=years,
                end_2028_value=terminal,
                october_2027_value=terminal/1.12**1.2,
                october_2026_value=terminal/1.12**2.2)

if __name__ == "__main__":
    cases = [model(name, case) for name,case in CASES.items()]
    assert abs(sum(c["assumptions"]["weight"] for c in cases)-1) < 1e-12
    output = dict(as_of="2026-10-22", currency="USD", units="billions except prices, GW and ratios",
                  probabilities="subjective conditional scenario weights; not empirical forecasts",
                  assumptions_common=dict(start_gw=1.85, legacy_revenue=19., start_debt=50.,
                      start_cash=3., start_shares=.600,
                      new_debt_fraction=.8, depreciation_years=6., legacy_annual_da=9.,
                      quarterly_legacy_principal=2.5, new_debt_amortization_quarters=20,
                      cash_tax_rate=.2, discount_rate=.12, sbc_fraction_of_revenue=.03,
                      utilization_after_ready=1.),
                  cases=cases,
                  weighted_october_2027=sum(c["assumptions"]["weight"]*c["october_2027_value"] for c in cases),
                  weighted_october_2026=sum(c["assumptions"]["weight"]*c["october_2026_value"] for c in cases),
                  base_new_equipment_eight_year_sensitivity=model("base_new_life_8", dict(CASES["base"], new_equipment_life=8.)))
    Path(__file__).with_suffix(".json").write_text(json.dumps(output, indent=2)+"\n")
    for c in cases:
        print(c["name"], json.dumps({"2027":c["years"]["2027"], "2028":c["years"]["2028"],
             "12m_value":c["october_2027_value"], "present_value":c["october_2026_value"]}))
    print("weighted", output["weighted_october_2027"], output["weighted_october_2026"])
