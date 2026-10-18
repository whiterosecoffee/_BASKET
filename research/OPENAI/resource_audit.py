#!/usr/bin/env python3
"""B13 source-readiness audit for OpenAI pre-IPO analysis (offline, deterministic).
No HTTP calls, price feeds, implicit API entitlement or automatic source promotion.
The score is factor *research importance*, NOT valuation, evidence coverage or
the probability of an IPO.
"""
import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FACTORS = {"revenue_quality","growth_durability","unit_economics",
           "capital_funding","competitive_position","governance_dilution",
           "market_price_discovery","compute_delivery"}
WORKING = {"CONNECTED_TESTED_OK"}
BLOCKED = {"NOT_ENTITLED_VERIFIED","NO_ENTITLED_TRANSACTION_FEED"}
NO_FEED = {"PUBLIC_API_DOCUMENTED_NOT_CONNECTED",
           "public_api_documented_connector_discovered_not_called",
           "web_accessible_not_scheduled",
           "WEB_ACCESSIBLE_NOT_API_INGESTED",
           "PUBLIC_EDGAR_FILING_ACCESS",
           "CONNECTOR_EXISTS_HISTORY_KNOWN_FUTURE_ENTITLEMENT_UNCHECKED",
           "ENDPOINT_DISCOVERED_ENTITLEMENT_UNCONFIRMED",
           "THIRD_PARTY_PLUGIN_AVAILABLE_NOT_CONNECTED",
           "SOURCE_BY_SOURCE_RESEARCH_NOT_FEED",
           "PUBLIC_ONLY_IF_FILED_AND_LISTED",
           "web_accessible_no_adapter"}


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def validate(registry, policy):
    if registry.get("schema") != "basket.openai_source_registry@1":
        raise ValueError("unexpected resource schema")
    if registry.get("not_a_live_data_system") is not True:
        raise ValueError("missing feed disclaimer")
    if registry.get("reporting_currency") != "USD":
        raise ValueError("non-USD reporting")
    if set(policy["factors"]) != FACTORS:
        raise ValueError("policy factor mismatch")
    names = set()
    for r in registry["sources"]:
        rid = r["id"]
        if rid in names:
            raise ValueError("duplicate source id " + rid)
        names.add(rid)
        if (not set(r["factors"]).issubset(FACTORS) or not r["factors"]
                or not r["url"].startswith("https://")
                or r["priority"] not in {"P0","P1","P2"}
                or not r["owner"] or not r["verified_today"]
                or r["access"] not in WORKING | BLOCKED | NO_FEED):
            raise ValueError("source missing required provenance/readiness: " + rid)
        if r["access"] in WORKING and "Called" not in r["verified_today"]:
            raise ValueError("verified entitlement needs recorded test evidence " + rid)
        if "private" in rid and "price" in r.get("measure", []):
            raise ValueError("private price must be sourced at security-class level")
    return {"source_count": len(names), "working_tested_sources":
            sum(r["access"] in WORKING for r in registry["sources"]),
            "not_entitled_sources":
            [r["id"] for r in registry["sources"] if r["access"] in BLOCKED]}


def weight_vector(policy, stage, regime):
    if stage not in policy["stages"] or regime not in policy["regime_adjustments"]:
        raise ValueError("stage/regime unknown")
    b = policy["stages"][stage]["base_weights_pct"]
    m = policy["regime_adjustments"][regime]["multipliers"]
    if set(b) != FACTORS or sum(b.values()) != 100:
        raise ValueError("invalid baseline weights")
    weighted = {k:b[k]*m.get(k,1) for k in FACTORS}
    total = sum(weighted.values())
    if total <= 0 or any(v <= 0 for v in weighted.values()):
        raise ValueError("invalid stage/regime normalization")
    return {k:100*weighted[k]/total for k in FACTORS}


def evaluate(registry, policy, as_of, stage="pre_prospectus", regime="neutral"):
    # Historical replay is expressly not supported without ingestion timestamps.
    if dt.date.fromisoformat(as_of) != dt.date.fromisoformat(registry["prepared_on"]):
        raise ValueError("registry is a dated static access snapshot; no as-of backfill")
    meta = validate(registry, policy)
    w = weight_vector(policy, stage, regime)
    if stage != "pre_prospectus":
        # Preview planning weights, not a claim of a verified public IPO stage.
        stage_status = "hypothetical_future_stage_NOT_VERIFIED"
    else:
        stage_status = "pre_prospectus_current_working_stage"
    factor_details = []
    for factor in sorted(FACTORS, key=lambda f:(-w[f],f)):
        candidates = [r for r in registry["sources"] if factor in r["factors"]]
        candidates.sort(key=lambda r:({"P0":0,"P1":1,"P2":2}[r["priority"]],
                                       0 if r["access"] in WORKING else 1,r["id"]))
        factor_details.append({
            "factor":factor,"research_weight_pct":round(w[factor],4),
            "candidate_source_ids":[r["id"] for r in candidates],
            "currently_tested_provider_ids":[r["id"] for r in candidates
                                             if r["access"] in WORKING],
            "fundamental_measurement_completeness":"NOT_ESTABLISHED",
            "missing_issuer_fundamentals_not_filled":True
        })
    ranked = sorted(registry["sources"],
                    key=lambda r:({"P0":0,"P1":1,"P2":2}[r["priority"]],
                                  -sum(w[f] for f in r["factors"]),r["id"]))
    actions = []
    for r in ranked:
        access = r["access"]
        if access in WORKING:
            next_step = "Wire owner-operated point-in-time adapter; timestamps, snapshots, TTD and source-specific rights still required"
        elif access in BLOCKED:
            next_step = "Resolve entitlement or use named primary-source fallback; do not silently substitute data"
        else:
            next_step = "Confirm direct-source response, security/contract semantics, access license and dated ingestion before promotion"
        actions.append({"source_id":r["id"],"owner":r["owner"],
                        "priority":r["priority"],"access_state":access,
                        "relevant_weight_sum_pct_NON_ADDITIVE":
                            round(sum(w[f] for f in r["factors"]),3),
                        "next_validation":next_step,"missing":r["missing"]})
    return {"as_of":as_of,"research_stage":stage,"stage_status":stage_status,
            "conditional_regime":regime,"regime_is_assumed_not_empirically_proven":True,
            "registry_version":registry["version"],"source_test_inventory":meta,
            "factors":factor_details,"source_validation_queue":actions,
            "is_live_feed":False,"IPO_probability":None,
            "OpenAI_fair_value_usd":None,"SFTBY_net_NAV":None,
            "note":"Source readiness is not measurement validity, and sum of overlapping source factor weights is NOT a confidence or investment score."}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--as-of",default="2026-10-17")
    p.add_argument("--stage",default="pre_prospectus")
    p.add_argument("--regime",default="neutral")
    args=p.parse_args()
    print(json.dumps(evaluate(load("resource-registry.json"),
                              load("ipo2027-policy.json"),
                              args.as_of,args.stage,args.regime),
                     sort_keys=True,indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError) as exc:
        raise SystemExit("Source registry validation failed: "+str(exc))
