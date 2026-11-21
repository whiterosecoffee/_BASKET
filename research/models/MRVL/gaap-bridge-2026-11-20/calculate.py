"""Bounded MRVL research calculator. USD millions unless per share."""
import json
import math
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION = "0.1.0"

def finite(v, positive=False):
    if isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v):
        raise ValueError("finite numeric input required")
    if positive and v <= 0:
        raise ValueError("positive numeric input required")
    return v

def calculate(data):
    historical = []
    for row in data["historical_m"]:
        deductions = sum(row[k] for k in ("sbc", "amort", "restructuring",
            "contingent_fair_value_net", "other", "tax_adjustment"))
        ni = row["adjusted_income"] - deductions
        historical.append({"period":row["period"], "gaap_income_m":round(ni, 8),
            "gaap_eps":ni / row["diluted_shares"],
            "income_reconciles":abs(ni-row["reported_gaap_income"]) < 1e-7})
    q = data["q3_guidance"]
    q3 = q["adjusted_eps"] - sum(q[k] for k in ("sbc","amort","tax_adjustment","other"))
    adj_tax = finite(data["adjusted_tax_assumption"])
    if not 0 <= adj_tax < 1:
        raise ValueError("invalid adjusted tax")
    price = finite(data["price_reference"]["usd"], True)
    forecast = []
    for p in data["periods"]:
        shares = finite(p["reference_diluted_shares_m"], True)
        adj_eps = finite(p["adjusted_eps"])
        revenue = finite(p["revenue_m"], True)
        adj_ni = adj_eps * shares
        adj_pti = adj_ni / (1-adj_tax)
        for c in data["cases"]:
            tax = finite(c["gaap_tax_rate"])
            rate = finite(c["sbc_revenue_rate"])
            if not 0 <= tax < 1 or not 0 <= rate <= 1:
                raise ValueError("invalid tax or compensation ratio")
            sbc = revenue * rate
            exclusion = sbc + p["scheduled_amort_m"] + c["new_iprd_amort_m"] + c["other_exclusions_m"]
            gaap_pti = adj_pti - exclusion
            # No tax-benefit assumption for a loss scenario.
            ni = gaap_pti * (1-tax) if gaap_pti > 0 else gaap_pti
            eps = ni / shares
            forecast.append({"fy":p["fy"],"calendar_proxy_for":p["calendar_proxy_for"],
                "case":c["name"],"classification":"conditional_standalone_sensitivity",
                "adjusted_eps_input":adj_eps,"adjusted_pe_reference":price/adj_eps if adj_eps>0 else None,
                "reference_diluted_shares_m":shares,"adjusted_profit_proxy_m":adj_ni,
                "adjusted_pretax_proxy_m":adj_pti,"sbc_m":sbc,
                "scheduled_amort_m":p["scheduled_amort_m"],"new_iprd_amort_m":c["new_iprd_amort_m"],
                "other_exclusions_m":c["other_exclusions_m"],"gaap_tax_rate":tax,
                "modeled_gaap_income_m":ni,"modeled_gaap_eps":eps,
                "modeled_gaap_pe":price/eps if eps>0 else None,
                "eps_with_5pct_extra_shares":ni/(shares*1.05)})
    digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return {"model_version":VERSION,"input_manifest_sha256":digest,"as_of_date":data["as_of_date"],
        "price_reference":data["price_reference"],"historical":historical,
        "q3_guidance_gaap_eps":round(q3,10),"forecast":forecast,
        "verification_gates":data["gates"],
        "calendar_identity":"CY2028 net income = FY2029 net income - January2029 net income + January2028 net income; recompute calendar weighted shares. Exact months unavailable.",
        "calendar_status":"FY2029 is only an approximately eleven-month-overlap proxy for CY2028, not exact calendar earnings."}

def verify(data, result):
    assert all(x["income_reconciles"] for x in result["historical"])
    assert abs(result["q3_guidance_gaap_eps"]-.53) < 1e-12
    for fy in (2028,2029):
        rows={x["case"]:x for x in result["forecast"] if x["fy"]==fy}
        assert rows["lower_cost"]["modeled_gaap_eps"] > rows["reference"]["modeled_gaap_eps"] > rows["higher_cost"]["modeled_gaap_eps"]
        for row in rows.values():
            assert row["eps_with_5pct_extra_shares"] < row["modeled_gaap_eps"]
    assert result == calculate(data)
    assert all(v is None for k,v in result["verification_gates"].items() if k.startswith("verified_"))
    for v in (True, float("nan"), float("inf")):
        try:
            finite(v)
        except ValueError:
            continue
        raise AssertionError("invalid number admitted")
    return "historical/Q3 reconciliation, cost/dilution direction, deterministic replay, null gates and finite input checks passed"

if __name__ == "__main__":
    inputs=json.loads((ROOT/"inputs.json").read_text())
    result=calculate(inputs)
    print(verify(inputs,result))
    (ROOT/"results.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    for r in result["forecast"]:
        print(f'FY{r["fy"]} {r["case"]}: modeled GAAP EPS {r["modeled_gaap_eps"]:.4f}; P/E {r["modeled_gaap_pe"]:.4f}')

