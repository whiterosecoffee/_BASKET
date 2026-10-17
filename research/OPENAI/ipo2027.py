#!/usr/bin/env python3
"""B13 research-only IPO 2027 adaptive measurements; deterministic and fail-closed.

This is NOT a B04 fundamental valuation engine, B09 NAV, B02 market feed,
a probability forecast, or a live 2027 OpenAI valuation.
"""
import argparse
import datetime as dt
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
FACTORS = ("revenue_quality", "growth_durability", "unit_economics",
           "capital_funding", "competitive_position", "governance_dilution",
           "market_price_discovery", "compute_delivery")


def date(x):
    return dt.date.fromisoformat(x)


def ensure(ok, message):
    if not ok:
        raise ValueError(message)


def read(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def verify(policy=None, news=None):
    policy = policy if policy is not None else read("ipo2027-policy.json")
    news = news if news is not None else read("ipo2027-news.json")
    ensure(policy["schema"] == "basket.openai_ipo_weight_policy@1"
           and news["schema"] == "basket.openai_ipo_news@1",
           "unexpected research contract")
    ensure(policy["currency"] == "USD" and policy["entity_id"] == "OPENAI",
           "issuer or currency mismatch")
    ensure(set(policy["factors"]) == set(FACTORS), "missing/extra factors")
    for key, stage in policy["stages"].items():
        values = stage["base_weights_pct"]
        ensure(set(values) == set(FACTORS), "stage factors: " + key)
        ensure(sum(values.values()) == 100 and all(v > 0 for v in values.values()),
               "weights must be positive and sum to 100")
    for key, regime in policy["regime_adjustments"].items():
        for factor, scale in regime["multipliers"].items():
            ensure(factor in FACTORS and math.isfinite(scale) and scale > 0,
                   "invalid regime: " + key)
    seen = set()
    for item in news["items"]:
        ensure(item["id"] not in seen, "duplicate news record")
        seen.add(item["id"])
        ensure(date(item["available_on"]) <= date(news["as_of_date"]),
               "future information in source catalog")
        ensure(item["source_url"].startswith("https://"), "missing news URL")
        ensure(item["temporal_precision"] == "date_only", "invented intraday precision")
        ensure(set(item["factor_ids"]).issubset(FACTORS), "unknown factor")
        ensure(item["verification_state"] and item["evidence_class"],
               "unclassified report")
    ensure(set(news["research_ids"]) == seen, "inconsistent news IDs")
    return {"policy_version": policy["policy_version"],
            "verified_news_records": len(seen), "factors": len(FACTORS),
            "stages": len(policy["stages"]), "regimes": len(policy["regime_adjustments"])}


def relevant_news(news, as_of):
    """Date-only: historical-day replay, not same-day timestamped quote validity."""
    return [s for s in news["items"] if date(s["available_on"]) <= date(as_of)]


def weights(policy, stage, regime):
    ensure(stage in policy["stages"], "unknown stage")
    ensure(regime in policy["regime_adjustments"], "unknown regime")
    base = policy["stages"][stage]["base_weights_pct"]
    mods = policy["regime_adjustments"][regime]["multipliers"]
    raw = {k: base[k] * mods.get(k, 1.0) for k in FACTORS}
    denominator = sum(raw.values())
    return {k: 100 * raw[k] / denominator for k in FACTORS}


def stage_gate(policy, stage, available):
    # No date-only story supports public prospectus or live price range.
    if stage == "pre_prospectus":
        return {"eligible": True, "state": "confidential_or_unpriced"}
    necessary = policy["stages"][stage]["proof"]
    # Proof cannot be self-declared or inferred from Reuters confidential filing.
    return {"eligible": False, "state": "blocked_missing_verified_stage_proof",
            "required": necessary,
            "detail": "Escalate to B03/B00 for regulator-stamped filing / official offer details."}


def rating_summary(weight, ratings, known_ids, as_of):
    """Scores are human research inputs, not outputs inferred from news."""
    if ratings is None:
        return {"coverage": 0, "observed_quality_score": None,
                "quality_interval": [0, 100], "status": "unrated"}
    weighted = rated_mass = 0.0
    for factor, x in ratings.items():
        ensure(factor in weight, "unknown rated factor")
        ensure(x["source_ids"] and all(s in known_ids for s in x["source_ids"]),
               "rating lacks point-in-time evidence")
        ensure(date(x["available_on"]) <= date(as_of), "rating lookahead")
        q, score = float(x["reliability"]), float(x["score"])
        ensure(math.isfinite(q) and 0 <= q <= 1 and math.isfinite(score)
               and 0 <= score <= 100, "rating out of range")
        mass = weight[factor] * q / 100
        rated_mass += mass
        weighted += mass * score
    observed = weighted / rated_mass if rated_mass else None
    # Unrated or untrusted evidence is genuinely unknown, not secretly 50.
    lower, upper = weighted, weighted + (1 - rated_mass) * 100
    return {"coverage": round(rated_mass, 5),
            "observed_quality_score": round(observed, 3) if observed is not None else None,
            "quality_interval": [round(lower, 3), round(upper, 3)],
            "status": "research_quality_only_not_equity_valuation",
            "note": "Interval is a logical missing-evidence envelope, NOT a calibrated confidence interval."}


def scenario(revenue, multiple, cash, debt, claims):
    """User-supplied, aligned 2027 forward revenue / EV-sales sensitivity."""
    for label, x in dict(forward_2027_revenue=revenue, multiple=multiple,
                         unrestricted_cash=cash, debt=debt,
                         other_senior_claims=claims).items():
        ensure(x is not None and math.isfinite(x) and x >= 0,
               "scenario requires nonnegative explicit " + label)
    ensure(revenue > 0 and multiple > 0, "invalid scenario revenue/multiple")
    ev = revenue * multiple
    equity = ev + cash - debt - claims
    return {
        "classification": "user_supplied_EV_multiple_scenario_not_fair_value",
        "inputs": {"normalized_forward_2027_revenue_usd_b": revenue,
                   "hypothetical_EV_to_revenue_multiple": multiple,
                   "unrestricted_cash_usd_b": cash,
                   "debt_usd_b": debt,
                   "senior_claims_usd_b": claims},
        "implied_EV_usd_b": round(ev, 4),
        "implied_equity_usd_b": round(equity, 4),
        "equity_floor_applied": False,
        "warning": "Assumptions are user supplied, NOT verified OpenAI accounts. Prefer separately modeled FCFF and funding/dilution. Do not add IPO proceeds without new-share dilution."
    }


def run(as_of, stage="pre_prospectus", regime="neutral",
        ratings=None, scenario_values=None):
    policy, news = read("ipo2027-policy.json"), read("ipo2027-news.json")
    meta = verify(policy, news)
    ensure(date(as_of) <= date(policy["as_of_date"]),
           "future-as-of requires refreshed evidence snapshot")
    available = relevant_news(news, as_of)
    gate = stage_gate(policy, stage, available)
    ensure(gate["eligible"], "stage blocked: " + gate["required"])
    w = weights(policy, stage, regime)
    if regime != "neutral":
        # A regime is explicitly an analyst condition, not 'proved' by mere article count.
        regime_flag = "conditional_user_selected_regime"
    else:
        regime_flag = "neutral"
    q = rating_summary(w, ratings, {e["id"] for e in available}, as_of)
    return {"as_of_date": as_of, "issuer_id": "OPENAI",
            "source_precision": "calendar_day_only_not_intraday",
            "engine_version": "B13-IPO-weights@0.1.0", "policy": meta,
            "stage": stage, "stage_gate": gate,
            "regime": regime, "regime_state": regime_flag,
            "weights_percent": {k: round(v, 5) for k, v in w.items()},
            "available_evidence_ids": [s["id"] for s in available],
            "evidence_quality": q,
            "valuation_readiness": "blocked_missing_audited_cashflow_security_class_EV_bridge",
            "conditional_EV_scenario": scenario(**scenario_values) if scenario_values else None,
            "net_SFTBY_NAV": None,
            "IPO_probability": None}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--as-of", default="2026-10-17")
    p.add_argument("--stage", default="pre_prospectus")
    p.add_argument("--regime", default="neutral")
    p.add_argument("--ratings-file")
    p.add_argument("--forward-revenue-usd-b", type=float)
    p.add_argument("--ev-revenue-multiple", type=float)
    p.add_argument("--unrestricted-cash-usd-b", type=float)
    p.add_argument("--debt-usd-b", type=float)
    p.add_argument("--senior-claims-usd-b", type=float)
    args = p.parse_args()
    args_names = ("forward_revenue_usd_b", "ev_revenue_multiple",
                  "unrestricted_cash_usd_b", "debt_usd_b", "senior_claims_usd_b")
    inputs = [getattr(args, k) for k in args_names]
    if any(x is not None for x in inputs) and any(x is None for x in inputs):
        p.error("Scenario requires all five numeric inputs including explicit cash, debt and claims")
    values = (dict(zip(("revenue", "multiple", "cash", "debt", "claims"), inputs))
              if all(x is not None for x in inputs) else None)
    ratings = json.loads(Path(args.ratings_file).read_text(encoding="utf-8")) if args.ratings_file else None
    print(json.dumps(run(args.as_of, args.stage, args.regime, ratings, values),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise SystemExit("IPO research check failed: " + str(exc))
