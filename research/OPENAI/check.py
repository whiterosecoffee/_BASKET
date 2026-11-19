#!/usr/bin/env python3
"""Offline B13 OPENAI pre-IPO evidence and conditional gross-sensitivity validator.

Research-only, not a B04 valuation or B09 NAV computation. Stdlib only.
Date-only source availability is intentional: no manufactured tick timestamps.
"""
import argparse
import datetime as dt
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
B13 = ROOT / "research" / "OPENAI"


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def date(value):
    return dt.date.fromisoformat(value)


def check(statement, explanation):
    if not statement:
        raise ValueError(explanation)


def validate():
    entity = read("tickers/OPENAI/entity.json")
    vr = read("research/OPENAI/valuation-register.json")
    interface = read("research/OPENAI/sftby-interface.json")
    assumptions = read("research/OPENAI/assumption-register.json")

    check(entity["schema"] == "entity@1" and entity["id"] == "OPENAI" and
          entity["type"] == "private_company" and entity["currency"] == "USD",
          "OPENAI cannot be presented as public equity")
    check(vr["schema"] == "basket.preipo_valuation_research@1" and
          vr["identity"]["exchange_ticker"] is None and
          vr["identity"]["public_ohlcv_eligible"] is False and
          vr["identity"]["tradable_equity"] is False, "invented public ticker eligibility")
    check(vr["reporting_currency"] == "USD" and
          vr.get("ingested_at_utc") is None, "unverified timestamp or foreign reporting unit")

    sources = vr["sources"]
    check(all(s.get("url", "").startswith("https://") for s in sources.values()),
          "all sources must be primary, traceable HTTPS URLs")
    ids = set()
    by_metric = {}
    for row in vr["observations"]:
        rid = row["id"]
        check(rid not in ids, "duplicate evidence id: " + rid)
        ids.add(rid)
        check(row["source_ids"] and all(s in sources for s in row["source_ids"]),
              "untraceable source on " + rid)
        check(date(row["available_on"]) >= date(row["observation_on"]),
              "future leak: available before observation for " + rid)
        check(date(row["available_on"]) <= date(vr["as_of_date"]),
              "registry contains future unavailable information: " + rid)
        check(row["unit"] in ("USD_billion", "USD_billion_per_year", "fraction"),
              "unhandled unit")
        check(isinstance(row["value"], (int, float)) and
              math.isfinite(row["value"]) and row["value"] >= 0,
              "invalid observed numeric value")
        check("reported_perp" not in row["measurement"] or
              row["status"] == "reported_only_not_transacted_equity",
              "synthetic market proxy falsely promoted to equity")
        by_metric[row["measurement"]] = row

    prem = by_metric["fundraising_round_pre_money_equity_value"]
    post = by_metric["fundraising_round_post_money_equity_value"]
    committed = by_metric["financing_round_committed_capital"]
    check(math.isclose(prem["value"] + committed["value"], post["value"]),
          "financing round misreconciled")
    check(post["basis"] == "primary_financing_equity_post_money" and
          prem["basis"] == "primary_financing_agreed_terms",
          "enterprise-equity accounting basis conflated")
    check(by_metric["reported_annualized_revenue_run_rate"]["approximate"] is True and
          "not_audited" in by_metric["reported_annualized_revenue_run_rate"]["basis"],
          "annualized sales must remain an explicitly provisional proxy")

    check(interface["schema"] == "basket.openai_sftby_interface@1" and
          interface["overall_state"] == "methodology_only_not_current_nav",
          "SFTBY scenario improperly promoted to live NAV")
    check(interface["acceptance_gate"]["current_eligibility"] ==
          "blocked_missing_required_inputs", "SFTBY net NAV prematurely published")
    check("SVF2" in interface["method"]["fundNAV_replacement"] and
          "current_SFTBY_NAV" in interface["blocked_outputs"],
          "SVF2 NAV double-counting guard absent")
    for s in interface["illustrative_scenarios"]:
        check(s["classification"].endswith("not_fair_value"),
              "hypothetical scenario conflated with fair value")
        value = s["assumed_openai_equity_value_usd_b"]
        fraction = s["assumed_openai_ownership_fraction"]
        pct = s["assumed_move_pct"]
        check(0 <= fraction <= 1, "unrealistic ownership fraction")
        check(math.isclose(s["gross_stake_value_usd_b"], value * fraction),
              "gross stake scenario arithmetic fails")
        check(math.isclose(s["gross_stake_move_usd_b"], value * fraction * pct / 100),
              "gross stake shock arithmetic fails")

    check(assumptions["schema"] == "basket.preipo_assumption_register@1",
          "assumptions registry contract mismatch")
    assumption_ids = set()
    for r in assumptions["items"]:
        check(r["id"] not in assumption_ids, "duplicate hypothesis id")
        assumption_ids.add(r["id"])
        check(r["source_url"].startswith("https://") and
              r["verification_checks"] and r["falsifiers"], "untestable hypothesis")

    # Protected old ticker.history.jsonl is allowed to contain private funding
    # observations someday, but never synthetic trade bars as public OHLCV.
    history = ROOT / "tickers" / "OPENAI" / "history.jsonl"
    if history.exists():
        for raw in history.read_text(encoding="utf-8").splitlines():
            if raw.strip():
                row = json.loads(raw)
                check(not ("open" in row and "high" in row and "low" in row and
                           "close" in row and "volume" in row),
                      "invented public OHLCV under private issuer")

    return {"state": "passed", "entity_id": "OPENAI",
            "evidence_count": len(ids), "assumptions_count": len(assumption_ids),
            "strict_issuer_state": "private_pre_ipo",
            "net_sftby_nav": "unavailable"}


def hypothetical(valuation, ownership, move, as_of):
    check(valuation > 0 and math.isfinite(valuation), "explicit positive valuation required")
    check(0 <= ownership <= 1 and math.isfinite(ownership), "invalid ownership input")
    check(math.isfinite(move), "invalid price-shock input")
    reg = read("research/OPENAI/valuation-register.json")
    investment = next(r for r in reg["observations"]
                      if r["measurement"] == "softbank_approx_openai_ownership")
    check(date(as_of) >= date(investment["available_on"]),
          "cannot use ownership first disclosed after requested as-of")
    check(date(as_of) <= date(reg["as_of_date"]),
          "future dates lack B13 research snapshot; update sources first")
    return {
        "classification": "conditional_gross_lookthrough_not_sftby_nav",
        "as_of_date": as_of,
        "assumed_company_equity_valuation_usd_b": valuation,
        "assumed_ownership_fraction": ownership,
        "valuation_move_percent": move,
        "gross_stake_value_usd_b": round(valuation * ownership, 6),
        "gross_stake_delta_usd_b": round(valuation * ownership * move / 100, 6),
        "ownership_source_id": investment["id"],
        "model_version": "B13-gross-stake@0.1.0",
        "net_parent_NAV_USD": None,
        "eligible_for_current_nav": False,
        "caveat": "Scenario only: no security-class waterfall, fund fee, base fund mark, adjusted debt or dilution. No price prediction."
    }


def self_test():
    a = hypothetical(852, 0.13, -4, "2026-10-17")
    check(math.isclose(a["gross_stake_value_usd_b"], 110.76),
          "baseline scenario regression")
    check(math.isclose(a["gross_stake_delta_usd_b"], -4.4304),
          "shock scenario regression")
    b = hypothetical(1500, 0.13, -4, "2026-10-17")
    check(math.isclose(b["gross_stake_value_usd_b"], 195), "perp proxy regression")
    check(math.isclose(b["gross_stake_delta_usd_b"], -7.8), "gross scenario regression")
    try:
        hypothetical(852, 0.13, -4, "2026-09-01")
    except ValueError:
        pass
    else:
        raise AssertionError("look-ahead regression failed")
    return {"scenario_regressions": 5, "state": "passed"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--validate", action="store_true")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--valuation-usd-b", type=float)
    p.add_argument("--stake-fraction", type=float)
    p.add_argument("--move-pct", type=float, default=-4)
    p.add_argument("--as-of", help="YYYY-MM-DD; only within verified research snapshot")
    a = p.parse_args()
    output = {"validation": validate()}
    if a.self_test:
        output["self_test"] = self_test()
    if a.valuation_usd_b is not None:
        check(a.as_of is not None and a.stake_fraction is not None,
              "--as-of and --stake-fraction are required for a scenario")
        output["scenario"] = hypothetical(
            a.valuation_usd_b, a.stake_fraction, a.move_pct, a.as_of)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, IndexError, OSError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
