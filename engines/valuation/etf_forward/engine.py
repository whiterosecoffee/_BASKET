"""Deterministic ETF forward look-through. Standard-library only, no data fetching.

Inputs: JSON with as_of, holdings_available_at, weights, financial estimate
availability, earnings and equity capitalization in consistent USD share units.
Outputs: weighted earnings yields, PE only with valid full coverage, scenario grid.
No synthetic fixture can be presented as observed market data.
"""
import hashlib
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

VERSION = "etf-forward@0.1.0"

def dec(value):
    if isinstance(value, bool) or value is None:
        raise ValueError("numeric value required")
    try:
        x = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("invalid decimal") from None
    if not x.is_finite():
        raise ValueError("nonfinite decimal")
    return x

def known_by(record_time, as_of):
    if not record_time:
        raise ValueError("availability timestamp required")
    a = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    t = datetime.fromisoformat(record_time.replace("Z", "+00:00"))
    if a.tzinfo is None or t.tzinfo is None:
        raise ValueError("timezone required")
    if t > a:
        raise ValueError("lookahead violation")

def analyze(data):
    required = ("as_of", "holdings_available_at", "holdings", "source_manifest")
    if any(k not in data for k in required):
        raise ValueError("missing required top-level input")
    known_by(data["holdings_available_at"], data["as_of"])
    if not data["source_manifest"]:
        raise ValueError("source manifest required")
    holdings = data["holdings"]
    if not holdings:
        raise ValueError("holdings required")
    years = ("2027", "2028")
    output = {}
    sum_weight = Decimal(0)
    exposures = []
    seen = set()
    for h in holdings:
        ticker = h["ticker"]
        if ticker in seen:
            raise ValueError("duplicate holding identifier")
        seen.add(ticker)
        w = dec(h["weight"])
        if w < 0 or w > 1:
            raise ValueError("weights must be in [0,1]")
        sum_weight += w
        exposures.append((h, w))
    if abs(sum_weight - 1) > Decimal("0.000001"):
        raise ValueError("all fund economic weights including cash must sum to one")
    for year in years:
        yield_total, coverage = Decimal(0), Decimal(0)
        contributions, missing = [], []
        for h, w in exposures:
            if h.get("asset_type", "equity") != "equity":
                missing.append(h["ticker"] + ":non_equity")
                continue
            e = h.get("estimates", {}).get(year)
            if not e:
                missing.append(h["ticker"] + ":missing_estimate")
                continue
            known_by(e.get("available_at"), data["as_of"])
            if e.get("calendar_year") != int(year):
                raise ValueError("uncalendarized fiscal estimates prohibited")
            if e.get("currency") != "USD" or h.get("market_cap_currency") != "USD":
                raise ValueError("currency must be explicit and USD-normalized")
            cap = dec(h["market_cap_usd"])
            if cap <= 0:
                raise ValueError("market capitalization must be positive")
            income = dec(e["net_income_usd"])
            y = w * income / cap
            yield_total += y
            coverage += w
            contributions.append({"ticker": h["ticker"], "weight": str(w),
                                  "earnings_yield_contribution": str(y),
                                  "positive_income": income > 0})
        full = coverage == Decimal(1)
        output[year] = {"coverage_weight": str(coverage),
                        "earnings_yield": str(yield_total),
                        "pe": str(Decimal(1) / yield_total) if full and yield_total > 0 else None,
                        "pe_status": "valid" if full and yield_total > 0 else "not_meaningful_or_incomplete",
                        "contributions": contributions, "missing": missing}
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return {"schema": "basket.etf_forward_output@1", "engine_version": VERSION,
            "input_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
            "as_of": data["as_of"], "source_manifest": data["source_manifest"],
            "years": output, "fixture_kind": data.get("fixture_kind", "unspecified"),
            "caveat": "Coverage is fund-weight coverage; do not treat partial earnings yield as full ETF PE."}

def sensitivity(earnings_yield, earnings_revisions, multiple_factors):
    """Conditional price-return delta excluding dividends, fees and turnover.
    Price ratio = (1 + earnings_revision) * multiple_factor.
    """
    y = dec(earnings_yield)
    if y <= 0:
        raise ValueError("positive base yield required for PE sensitivity")
    rows = []
    for er in earnings_revisions:
        e = dec(er)
        if e <= -1:
            raise ValueError("revision must exceed -100%")
        for mf in multiple_factors:
            m = dec(mf)
            if m <= 0:
                raise ValueError("multiple factor must be positive")
            rows.append({"earnings_revision": str(e), "multiple_factor": str(m),
                         "price_return_ex_distributions": str((1 + e) * m - 1),
                         "earnings_component": str(e),
                         "multiple_component": str(m - 1),
                         "interaction": str(e * (m - 1))})
    return rows

def main():
    import argparse
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = analyze(json.loads(args.input.read_text()))
    result["sensitivity"] = sensitivity(result["years"]["2027"]["earnings_yield"],
                                        ["-0.2", "0", "0.2"], ["0.7", "1", "1.3"]) if result["years"]["2027"]["pe"] else []
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n")
    else:
        print(rendered)

if __name__ == "__main__":
    main()
