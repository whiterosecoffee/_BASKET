"""Point-in-time ETF economic look-through with explicit non-equity positions.
Pure, offline, USD-only component. Upstream owners normalize FX/share classes.
"""
import hashlib
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

VERSION = "etf-lookthrough@0.1.0"
YEARS = ("2027", "2028")
TOL = Decimal("0.000001")

def number(value):
    if value is None or isinstance(value, bool):
        raise ValueError("finite numeric value required")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("invalid numeric value") from None
    if not result.is_finite():
        raise ValueError("non-finite value")
    return result

def instant(value):
    if not isinstance(value, str):
        raise ValueError("timestamp required")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("invalid timestamp") from None
    if result.tzinfo is None:
        raise ValueError("timezone offset required")
    return result

def before_or_at(value, asof):
    if instant(value) > asof:
        raise ValueError("future-available input")

def calculate(snapshot):
    """CY2027/28 weighted earnings yield, guarded P/E; cash assumed zero yield.
    Derivatives and other assets fail closed until full fund accounting exists.
    """
    asof = instant(snapshot["as_of"])
    if snapshot.get("data_kind") not in ("verified_observation", "synthetic_test"):
        raise ValueError("data kind required")
    manifest = snapshot.get("source_manifest")
    if not isinstance(manifest, list) or not manifest:
        raise ValueError("nonempty source manifest required")
    before_or_at(snapshot["holdings_available_at"], asof)
    holdings = snapshot["holdings"]
    if not holdings:
        raise ValueError("nonempty holdings required")
    seen = set()
    weights = []
    for item in holdings:
        ticker = item["id"]
        if not ticker or ticker in seen:
            raise ValueError("invalid or duplicated holding")
        seen.add(ticker)
        before_or_at(item["available_at"], asof)
        weight = number(item["weight"])
        if not 0 <= weight <= 1:
            raise ValueError("invalid weight")
        category = item.get("asset_type")
        if category not in ("equity", "cash"):
            raise ValueError("unsupported asset type")
        if category == "cash" and item.get("currency") != "USD":
            raise ValueError("cash must be USD")
        weights.append((item, weight))
    total = sum((weight for _, weight in weights), Decimal(0))
    if abs(total - 1) > TOL:
        raise ValueError("portfolio weights must reconcile")
    response = {}
    for year in YEARS:
        yield_sum = Decimal(0)
        equity_total = Decimal(0)
        equity_covered = Decimal(0)
        missing = []
        contributors = []
        for item, weight in weights:
            if item["asset_type"] == "cash":
                contributors.append({"id": item["id"], "weight": str(weight),
                                     "contribution": "0", "status": "cash_zero_yield_assumption"})
                continue
            equity_total += weight
            estimate = item.get("estimates", {}).get(year)
            if estimate is None:
                missing.append(item["id"])
                continue
            before_or_at(estimate["available_at"], asof)
            if estimate.get("calendar_year") != int(year):
                raise ValueError("calendar-year mismatch")
            if item.get("equity_currency") != "USD" or estimate.get("currency") != "USD":
                raise ValueError("explicit USD normalization required")
            cap = number(item["market_cap_usd"])
            income = number(estimate["net_income_usd"])
            if cap <= 0:
                raise ValueError("positive equity capitalization required")
            contribution = weight * income / cap
            yield_sum += contribution
            equity_covered += weight
            contributors.append({"id": item["id"], "weight": str(weight),
                                 "contribution": str(contribution),
                                 "status": "loss" if income < 0 else "covered"})
        fully_covered = abs(equity_covered - equity_total) <= TOL
        valid_pe = fully_covered and yield_sum > 0
        response[year] = {
            "earnings_yield_known_contribution": str(yield_sum),
            "equity_weight": str(equity_total),
            "covered_equity_weight": str(equity_covered),
            "equity_coverage_ratio": str(equity_covered/equity_total) if equity_total else None,
            "portfolio_weight_covered": str(equity_covered + (1 - equity_total)),
            "pe": str(1 / yield_sum) if valid_pe else None,
            "pe_status": "valid_including_zero_yield_cash" if valid_pe else "incomplete_or_nonpositive",
            "missing_equity_ids": missing,
            "contributions": contributors,
        }
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return {"schema": "basket.etf_lookthrough@1", "engine_version": VERSION,
            "data_kind": snapshot["data_kind"], "as_of": snapshot["as_of"],
            "source_manifest": manifest, "input_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
            "years": response, "caveat": "No FX/ADR conversions; zero-yield cash assumption; no fee, distributions, tracking or derivative valuation."}
