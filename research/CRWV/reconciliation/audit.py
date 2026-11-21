"""CRWV source reconciliation, not a forecast or a second funding engine."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path

VERSION = "crwv-reconciliation@0.1.0"


def number(value):
    if value is None or isinstance(value, bool):
        raise ValueError("required numeric input missing or boolean")
    n = Decimal(str(value))
    if not n.is_finite():
        raise ValueError("non-finite input")
    return n


def instant(value):
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("timezone required")
    return d.astimezone(timezone.utc)


def total(values):
    return sum((number(v) for v in values), Decimal(0))


def close(actual, expected, tolerance="0.01"):
    if abs(actual - number(expected)) > Decimal(tolerance):
        raise ValueError(f"bridge does not reconcile: {actual} != {expected}")


def source_state(source, as_of):
    available = source.get("available_at")
    if available is None:
        return "availability_unknown"
    return "available" if instant(available) <= instant(as_of) else "future"


def earnings_bridge(q):
    """USD millions; SBC remains an expense in the GAAP branch."""
    gaap = number(q["operating_income_m"]) - number(q["net_interest_m"]) + number(q["other_income_m"]) - number(q["tax_m"])
    close(gaap, q["gaap_net_income_m"])
    adjusted = gaap + total(q["adjustments_m"].values())
    close(adjusted, q["adjusted_net_income_m"])
    shares = number(q["weighted_average_shares_m"])
    if shares <= 0:
        raise ValueError("positive weighted shares required")
    close(gaap / shares, q["reported_gaap_eps"], "0.01")
    return {"gaap_net_income_m": float(gaap), "adjusted_net_income_m": float(adjusted),
            "gaap_eps_calculated": float(gaap / shares),
            "adjusted_eps_calculated": float(adjusted / shares),
            "adjustment_total_m": float(adjusted - gaap),
            "note": "Adjusted EPS is arithmetic on reported rounded income/shares, not company EPS guidance."}


def balance_bridge(b):
    """Debt carrying value differs from principal; lease definitions stay explicit."""
    debt = total(b["debt_carrying_components_m"].values())
    principal = total(b["principal_schedule_m"].values())
    close(principal - debt, b["unamortized_discount_and_costs_m"])
    finance_leases = total(b["finance_leases_m"].values())
    operating_leases = total(b["operating_leases_m"].values())
    liquid = number(b["unrestricted_cash_m"]) + number(b["marketable_securities_m"])
    restricted = total(b["restricted_cash_m"].values())
    return {"period_end": b["period_end"], "debt_carrying_m": float(debt),
            "debt_principal_m": float(principal), "finance_leases_m": float(finance_leases),
            "operating_leases_m": float(operating_leases), "restricted_cash_excluded_m": float(restricted),
            "net_debt_with_finance_leases_m": float(debt + finance_leases - liquid),
            "lease_inclusive_net_obligations_m": float(debt + finance_leases + operating_leases - liquid),
            "current_balance_verified": False,
            "note": "Historical balance; lease-inclusive obligations are not interchangeable with standard EV."}


def cash_bridge(c):
    end = number(c["opening_total_cash_m"]) + number(c["operating_cash_flow_m"]) + number(c["investing_cash_flow_m"]) + number(c["financing_cash_flow_m"])
    close(end, c["closing_total_cash_m"])
    return {"closing_total_cash_m": float(end),
            "operating_cash_less_cash_ppe_purchases_m": float(number(c["operating_cash_flow_m"]) - number(c["cash_ppe_purchases_m"])),
            "operating_cash_excluding_deferred_revenue_change_m": float(number(c["operating_cash_flow_m"]) - number(c["deferred_revenue_change_m"])),
            "note": "Excluding deferred-revenue change is a mechanical sensitivity, not normalized operating cash flow; cash PPE purchases differ from reported total capex."}


def forward_audit(row, price, as_of, source):
    if source_state(source, as_of) == "future":
        return {"source_id": row["source_id"], "fiscal_year": row["fiscal_year"],
                "reported_eps": None, "basis": None, "status": "future",
                "diagnostic_price_over_reported_eps": None, "verified_gaap_pe": None,
                "unexplained_pretax_residual_m": None,
                "reasons": ["source is unavailable at requested cutoff"],
                "note": "Future estimate values excluded, not merely labelled unverified."}
    eps = number(row["eps"]) if row.get("eps") is not None else None
    reasons = []
    if row.get("basis") != "gaap":
        reasons.append("GAAP accounting basis not established")
    if source_state(source, as_of) != "available":
        reasons.append("point-in-time source availability not established")
    ni, shares = row.get("net_income_m"), row.get("diluted_shares_m")
    if ni is None or shares is None:
        reasons.append("matching net income and forecast diluted shares missing")
    elif number(shares) <= 0:
        raise ValueError("positive forecast shares required")
    elif eps is None or abs(number(ni) / number(shares) - eps) > Decimal("0.02"):
        reasons.append("EPS does not reconcile to same-basis net income/shares")
    residual = None
    if all(row.get(k) is not None for k in ("ebit_m", "interest_m", "pretax_income_m")):
        residual = number(row["pretax_income_m"]) - (number(row["ebit_m"]) - number(row["interest_m"]))
        if residual != 0 and row.get("other_pretax_items_m") is None:
            reasons.append("unexplained pretax reconciliation residual")
        elif row.get("other_pretax_items_m") is not None:
            close(residual, row["other_pretax_items_m"])
    positive = eps is not None and eps > 0
    ratio = float(number(price) / eps) if positive else None
    return {"source_id": row["source_id"], "fiscal_year": row["fiscal_year"],
            "reported_eps": float(eps) if eps is not None else None,
            "basis": row.get("basis", "unknown"), "status": "unqualified" if reasons else "reconciled",
            "diagnostic_price_over_reported_eps": ratio,
            "verified_gaap_pe": ratio if not reasons else None,
            "unexplained_pretax_residual_m": float(residual) if residual is not None else None,
            "reasons": reasons,
            "note": "Diagnostic ratio is not an accepted forward multiple; losses have no meaningful positive P/E."}


def funding_readiness(f):
    """Validate completeness only. Monthly cash simulation remains #86's job."""
    required = ("opening_unrestricted_cash_m", "monthly_uses", "committed_draw_conditions",
                "prepayment_receipts", "restricted_cash_release_conditions", "covenant_headroom")
    missing = [k for k in required if f.get(k) is None]
    for receipt in f.get("prepayment_receipts") or []:
        if receipt.get("status") != "received" or not receipt.get("received_at"):
            missing.append("prepayment receipt completion evidence")
    return {"status": "insufficient_inputs" if missing else "ready_for_owner_evaluation",
            "funding_gap_m": None, "fully_funded": None,
            "missing": missing,
            "note": "An aggregate liquidity figure, expected deposits or an unclosed facility cannot prove monthly funding feasibility."}


def evaluate(data, as_of):
    instant(as_of)
    for s in data["sources"].values():
        # Validate declared dates even when a source is not used in a calculation.
        if s.get("available_at"):
            instant(s["available_at"])
    price = number(data["price_reference"]["price_usd"])
    shares = number(data["price_reference"]["shares_outstanding_m"])
    if price <= 0 or shares <= 0:
        raise ValueError("positive price/shares required")
    if instant(data["price_reference"]["observed_at"]) > instant(as_of):
        raise ValueError("future price")
    sources = data["sources"]
    groups = {}
    for group, function in (("earnings", earnings_bridge), ("balance", balance_bridge), ("cash", cash_bridge)):
        entry = data[group]
        status = source_state(sources[entry["source_id"]], as_of)
        groups[group] = function(entry) if status == "available" else {"status": status, "value": None}
    rows = [forward_audit(r, price, as_of, sources[r["source_id"]]) for r in data["forward_estimates"]]
    cap = price * shares
    b = groups["balance"]
    return {"method_version": VERSION, "as_of": as_of,
            "input_sha256": hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest(),
            "currency": "USD", "amount_unit": "USD million unless EPS/price",
            "price_reference": data["price_reference"], "market_cap_reference_m": float(cap),
            "historical_balance_ev_reference_m": float(cap + number(b["net_debt_with_finance_leases_m"])) if "net_debt_with_finance_leases_m" in b else None,
            "ev_status": "mixed_date_illustration_not_current_EV", **groups,
            "forward_estimates": rows,
            "funding_readiness": funding_readiness(data["funding"]),
            "source_states": {k: source_state(v, as_of) for k, v in sources.items()},
            "unknowns": data["unknowns"]}


def render(result):
    lines = [f"CRWV reconciliation | {VERSION} | as of {result['as_of']}",
             f"Reference equity value USD {result['market_cap_reference_m']/1000:.3f}B; EV is a mixed-date illustration."]
    for r in result["forward_estimates"]:
        lines.append(f"{r['source_id']} FY{r['fiscal_year']}: reported EPS {r['reported_eps']}; verified GAAP P/E {r['verified_gaap_pe']}; {r['status']}: " + "; ".join(r["reasons"]))
    lines.append("Funding: " + result["funding_readiness"]["status"] + "; fully funded = unknown")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--as-of", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = evaluate(json.loads(args.input.read_text()), args.as_of)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "result.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (args.output / "result.txt").write_text(render(result))
    print(render(result), end="")
