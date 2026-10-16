#!/usr/bin/env python3
"""_BASKET narrative intelligence: append-only evidence and conditional extrapolation.
No network, hidden live feeds, or subjective probabilities. Stdlib only.
"""
import argparse
import datetime as dt
import json
import pathlib
import sys

UTC = dt.timezone.utc
KINDS = {"fact", "claim", "hypothesis", "perspective"}
STATES = {"confirmed", "reported", "unverified", "disputed", "supported",
          "contradicted", "unresolved", "rejected"}
REQUIRED = {"id", "kind", "entity", "metric", "value", "unit", "observed_at",
            "available_at", "ttd_seconds", "source", "basis", "status"}


def when(value):
    t = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("timezone-aware date required")
    return t.astimezone(UTC)


def iso(t):
    return t.astimezone(UTC).isoformat().replace("+00:00", "Z")


def validate(r):
    missing = REQUIRED - set(r)
    if missing:
        raise ValueError("missing fields: " + ", ".join(sorted(missing)))
    if r["kind"] not in KINDS or r["status"] not in STATES:
        raise ValueError("invalid kind/status")
    if not isinstance(r["ttd_seconds"], int) or r["ttd_seconds"] < 0:
        raise ValueError("invalid time-to-die")
    if not isinstance(r["source"], dict) or not r["source"].get("url"):
        raise ValueError("source URL required")
    if r["source"].get("tier") not in ("primary", "reporting", "commentary"):
        raise ValueError("source tier required")
    if r["kind"] == "hypothesis" and not r.get("falsifiers"):
        raise ValueError("hypothesis requires falsifiers")
    if when(r["available_at"]) < when(r["observed_at"]):
        raise ValueError("available_at before observed_at")
    if r["unit"] == "USD" and r.get("currency", "USD") != "USD":
        raise ValueError("mixed currency without conversion")
    return r


def load(path):
    records = []
    seen = set()
    with pathlib.Path(path).open(encoding="utf-8") as file:
        for n, line in enumerate(file, 1):
            if not line.strip():
                continue
            try:
                r = validate(json.loads(line))
            except (ValueError, json.JSONDecodeError) as e:
                raise ValueError("invalid JSONL line %d: %s" % (n, e)) from e
            if r["id"] in seen:
                raise ValueError("duplicate record ID: " + r["id"])
            seen.add(r["id"])
            records.append(r)
    return records


def freshness(r, asof):
    observed, available = when(r["observed_at"]), when(r["available_at"])
    if asof < available:
        return "not_yet_available"
    if observed > asof:
        return "lookahead_invalid"
    dead_at = observed + dt.timedelta(seconds=r["ttd_seconds"])
    return "alive" if asof < dead_at else "dead"


def audit(records, asof):
    known = {r["id"] for r in records if freshness(r, asof) == "alive"}
    items = []
    for r in records:
        state = freshness(r, asof)
        flags = []
        if state != "alive":
            flags.append("TTD_" + state.upper())
        if r["kind"] == "claim" and r["status"] != "confirmed":
            flags.append("SOURCE_REPORTED_NOT_VERIFIED")
        if r["kind"] == "hypothesis":
            flags.append("CAUSAL_OR_FORWARD_HYPOTHESIS")
            if any(d not in known for d in r.get("dependencies", [])):
                flags.append("MISSING_OR_EXPIRED_EVIDENCE")
        if r.get("basis") == "perp_implied_private_valuation":
            flags += ["NOT_TRANSACTED_EQUITY", "VERIFY_ORACLE_AND_CONTRACT",
                      "VERIFY_ORDER_BOOK_DEPTH"]
        if r.get("basis") == "bond_secondary_yield":
            flags.append("YTM_NOT_EXISTING_DEBT_COUPON")
        if r.get("basis") == "reported_rpo":
            flags.append("RPO_NOT_CASH_OR_MARGIN")
        if r.get("basis") == "article_causal_attribution":
            flags.append("CORRELATION_NOT_CAUSATION")
        items.append({"id": r["id"], "entity": r["entity"], "metric": r["metric"],
                      "kind": r["kind"], "evidence_status": r["status"],
                      "freshness": state, "flags": sorted(set(flags)),
                      "source_url": r["source"]["url"],
                      "caveat": r.get("caveat", "")})
    return {"evaluated_at": iso(asof), "records": items}


def extrapolate(records, asof):
    # Qualified model inputs must be exact SEC filing facts, within TTD.
    values = {}
    for r in records:
        if (r["entity"] == "CRWV" and r["kind"] == "fact" and
            r["status"] == "confirmed" and r["source"]["tier"] == "primary" and
            freshness(r, asof) == "alive" and isinstance(r["value"], (int, float))):
            values[r["metric"]] = r
    outputs = []
    def calc(name, value, unit, formula, source_records, interpretation):
        outputs.append({"metric": name, "value": round(value, 4),
                        "unit": unit, "formula": formula,
                        "inputs": [r["id"] for r in source_records],
                        "as_of": iso(asof), "classification": "conditional_derivation",
                        "caveat": interpretation})
    keys = ("rpo_usd_b", "rpo_0_24_fraction", "rpo_25_48_fraction")
    if all(k in values for k in keys):
        total, f1, f2 = [values[k] for k in keys]
        if not 0 <= f1["value"] + f2["value"] <= 1:
            raise ValueError("invalid RPO bucket shares")
        s = [total, f1, f2]
        calc("rpo_0_24_usd_b", total["value"] * f1["value"],
             "USD_billion", "RPO × 0–24-month fraction", s,
             "Expected RPO recognition, not cash, contracted profit or guaranteed delivery.")
        calc("rpo_25_48_usd_b", total["value"] * f2["value"],
             "USD_billion", "RPO × 25–48-month fraction", s,
             "Subject to performance obligations, deployment and reporting revisions.")
        calc("rpo_49_78_usd_b", total["value"] * (1 - f1["value"] - f2["value"]),
             "USD_billion", "RPO × residual fraction", s,
             "Residual calculation uses rounded disclosure percentages.")
        calc("rpo_0_24_annualized_usd_b", total["value"] * f1["value"] / 2,
             "USD_billion_per_year", "RPO × initial fraction / 2 years", s,
             "Bucket average only; NOT an actual annual revenue forecast.")
    if "liquidity_usd_b" in values and "undrawn_facilities_usd_b" in values:
        total, undrawn = values["liquidity_usd_b"], values["undrawn_facilities_usd_b"]
        calc("reported_liquidity_excluding_undrawn_usd_b", total["value"]-undrawn["value"],
             "USD_billion", "reported liquidity minus undrawn borrowing availability",
             [total, undrawn], "Includes cash and marketable securities; not net liquidity.")
    if all(k in values for k in ("customer_top1_fraction", "customer_top2_fraction",
                                  "customer_top3_fraction")):
        r = [values[k] for k in ("customer_top1_fraction", "customer_top2_fraction",
                                 "customer_top3_fraction")]
        calc("top3_customer_revenue_concentration_fraction", sum(v["value"] for v in r),
             "fraction", "sum of disclosed top-3 quarterly revenue shares", r,
             "Customer labels may change between reporting periods.")
    # Never apply observed bond yields to all existing debt automatically.
    calc("refinancing_100bp_per_10b_usd_b_annual", 0.1, "USD_billion_per_year",
         "$10B refinanced × 0.01 rate increase", [],
         "Sensitivity illustration ONLY; assumes $10B refinanced, all else equal.")
    return {"evaluated_at": iso(asof), "derived": outputs,
            "not_computed": ["private_fundamental_valuation",
                             "default_probability", "OpenAI_CRWV_causal_effect",
                             "customer_level_cashflow_without_disclosures"]}



def sensitivity(records, asof, private_equity_valuation_usd_b, valuation_move_pct):
    """Explicit SFTBY look-through scenario, NEVER a reported or current NAV mark."""
    if private_equity_valuation_usd_b <= 0:
        raise ValueError("valuation must be positive")
    shares = [r for r in records if
              r["entity"] == "SFTBY" and r["metric"] == "OPENAI_ownership_fraction"
              and r["kind"] == "fact" and r["status"] == "confirmed"
              and r["source"]["tier"] == "primary" and freshness(r, asof) == "alive"]
    if not shares:
        return {"evaluated_at": iso(asof), "state": "unavailable",
                "reason": "No live primary verified SFTBY ownership input"}
    sh = sorted(shares, key=lambda r: r["observed_at"])[-1]
    percent = sh["value"]
    if not 0 <= percent <= 1:
        raise ValueError("invalid ownership fraction")
    return {
        "evaluated_at": iso(asof), "classification": "conditional_sensitivity_not_NAV",
        "inputs": [sh["id"]], "scenario_assumptions": {
            "OPENAI_equity_valuation_usd_b": private_equity_valuation_usd_b,
            "valuation_move_pct": valuation_move_pct,
            "unchanged_ownership_fraction": percent,
            "fx": "USD-native; no conversion performed"
        },
        "gross_stake_value_usd_b": round(percent * private_equity_valuation_usd_b, 4),
        "gross_stake_change_usd_b": round(
            percent * private_equity_valuation_usd_b * valuation_move_pct / 100, 4),
        "caveat": "Not SoftBank NAV or accounting fair value. Ignores security preferences, fund-level economics, dilution, financing, tax, control and private-company illiquidity."
    }

def append(path, new):
    validate(new)
    p = pathlib.Path(path)
    existing = load(p) if p.exists() else []
    if new["id"] in {r["id"] for r in existing}:
        raise ValueError("duplicate ID: append requires distinct immutable record ID")
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(new, sort_keys=True, separators=(",", ":")) + "\n")
        f.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("audit", "extrapolate", "sensitivity", "append"))
    parser.add_argument("jsonl")
    parser.add_argument("--at", help="UTC evaluation timestamp (required for reproducible replay)")
    parser.add_argument("--input", help="JSON file with new record for append")
    parser.add_argument("--valuation-usd-b", type=float, help="Explicit hypothetical OpenAI equity valuation in USD billions")
    parser.add_argument("--move-pct", type=float, default=-4.0, help="Hypothetical valuation move in percentage points")
    args = parser.parse_args()
    if args.action == "append":
        if not args.input:
            parser.error("--input is required for append")
        append(args.jsonl, json.loads(pathlib.Path(args.input).read_text(encoding="utf-8")))
        print("appended")
        return
    if not args.at:
        parser.error("--at is required: do not use implicit clock for research replay")
    rows, instant = load(args.jsonl), when(args.at)
    if args.action == "audit":
        result = audit(rows, instant)
    elif args.action == "extrapolate":
        result = extrapolate(rows, instant)
    else:
        if args.valuation_usd_b is None:
            parser.error("--valuation-usd-b required for sensitivity")
        result = sensitivity(rows, instant, args.valuation_usd_b, args.move_pct)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
