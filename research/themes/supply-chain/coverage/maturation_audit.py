#!/usr/bin/env python3
"""B19 read-only maturation audit. Never promotes research hypotheses to economic facts."""
import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

class MaturityError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise MaturityError(message)

def canonical_digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def assess(mapping, pools):
    require(isinstance(mapping, dict) and mapping.get("schema") == "basket.b19-whole-basket-role-map@research1", "unsupported map contract")
    require(isinstance(pools, dict) and isinstance(pools.get("pools"), list), "unsupported pool inventory")
    rows = mapping.get("rows")
    require(isinstance(rows, list) and rows, "empty or invalid basket")
    pool_names = [p.get("id") for p in pools["pools"] if isinstance(p, dict)]
    require(len(pool_names) == len(pools["pools"]) and len(set(pool_names)) == len(pool_names)
            and all(isinstance(x, str) and x for x in pool_names), "bad pool IDs")
    known = set(pool_names)
    seen = set()
    memberships = Counter()
    issuers = 0
    role_covered = 0
    for row in rows:
        require(isinstance(row, dict), "non-object map row")
        sid = row.get("symbol")
        require(isinstance(sid, str) and sid and sid not in seen, "missing or duplicate symbol")
        seen.add(sid)
        typ = row.get("instrument_type", "")
        require(isinstance(typ, str), f"{sid}: missing instrument class")
        is_issuer = "equity" in typ or "receipt" in typ
        ids = row.get("pool_ids")
        require(isinstance(ids, list) and len(ids) == len(set(ids)), f"{sid}: duplicate or invalid pool list")
        require(set(ids) <= known, f"{sid}: unknown pool")
        roles = row.get("cross_cutting_roles", [])
        require(isinstance(roles, list), f"{sid}: invalid cross-cutting roles")
        require(is_issuer or (not ids and not roles), f"{sid}: nonissuer assigned issuer activity")
        require(row.get("contract_edges") == [] and row.get("source_supported_revenue_usd") is None
                and row.get("captured_share") is None and row.get("production_capacity") is None,
                f"{sid}: unsupported verified claim in provisional map")
        if is_issuer:
            issuers += 1
            if ids or roles:
                role_covered += 1
        memberships.update(ids)
    count = len(rows)
    require(mapping.get("authoritative_scope", {}).get("count") == count, "map count inconsistent with scope")
    require(mapping.get("pool_reference", {}).get("pool_count") == len(pool_names), "pool count inconsistent")
    require(mapping.get("coverage", {}).get("pool_participant_counts") ==
            {p: memberships[p] for p in pool_names}, "stale membership summary")
    for section, label in (("authoritative_scope", "instrument"), ("pool_reference", "pool")):
        revision = mapping.get(section, {}).get("head_sha")
        require(isinstance(revision, str) and re.fullmatch(r"[0-9a-f]{40}", revision) is not None, f"invalid pinned {label} SHA")
    reported_denominators = 0
    result_pools = []
    for p in pools["pools"]:
        pid = p["id"]
        amount = p.get("quarterly_final_demand_usd")
        refs = p.get("evidence_refs")
        state = p.get("status")
        require(isinstance(refs, list), f"{pid}: evidence refs missing")
        if state == "unmeasured":
            require(amount is None, f"{pid}: unmeasured pool has value")
        if amount is None:
            economic_state = "unmeasured"
        else:
            require(isinstance(amount, (int, float)) and not isinstance(amount, bool)
                    and math.isfinite(amount) and amount >= 0, f"{pid}: invalid demand")
            require(refs, f"{pid}: dollar amount without evidence references")
            reported_denominators += 1
            economic_state = "denominator_reported_attribution_unverified"
        result_pools.append({
            "pool_id": pid, "provisional_participants": memberships[pid],
            "buyer_dollar_coverage_ratio": None, "source_supported_attributed_usd": None,
            "tier1_coverage_ratio": None, "tier2_coverage_ratio": None,
            "economic_state": economic_state,
            "research_next": "Identify payer, purpose, fiscal period, qualified alternatives, evidenced budget and vendor awards; then tier1/tier2 purchases."
        })
    result_pools.sort(key=lambda x: (-x["provisional_participants"], x["pool_id"]))
    phases = [
        {"order": 1, "owner": "B19 #21", "action": "Validate pinned whole-basket research projection", "gate": "Deterministic IDs and pool references; no promoted claims"},
        {"order": 2, "owner": "B01 #52", "action": "Run independent B19 exact-head tests and pinned-input checks", "gate": "Required CI passes on exact SHA"},
        {"order": 3, "owner": "B00 #50", "action": "Arbitrate buyer-purpose pool and transaction keys using existing architecture", "gate": "Approved contract without new canonical store"},
        {"order": 4, "owner": "B19 #17 + B03", "action": "Source buyer-specific budgets and captured supplier awards across pool topics", "gate": "Period, source and economic state; unknown allocations null"},
        {"order": 5, "owner": "B05 #51", "action": "Traverse sourced buyer-to-supplier relationships and alternatives", "gate": "As-of evidence and duplicate-spending rejection"},
        {"order": 6, "owner": "B01 #52", "action": "Validate financial/temporal/physical capacity evidence and nonadditivity", "gate": "Exact-head positive and negative CI"},
        {"order": 7, "owner": "B00 #136", "action": "Review acceptance and integration sequence when authorized", "gate": "Authorized merge and green main CI"}
    ]
    return {
        "schema": "basket.b19-maturation-audit@research1",
        "input_fingerprint": canonical_digest({"map": mapping, "pools": pools}),
        "inputs": {"instrument_source_pr_head": mapping["authoritative_scope"]["head_sha"],
                   "pool_source_pr_head": mapping["pool_reference"]["head_sha"]},
        "scope": {"tracked_instruments": count, "equity_receipt_like": issuers,
                  "nonissuer": count - issuers, "provisionally_assigned_issuers": role_covered,
                  "unique_pool_memberships": sum(memberships.values()), "pool_topics": len(pool_names)},
        "financial_coverage": {"reported_denominator_pools": reported_denominators,
                               "verified_supplier_attribution_pools": 0,
                               "pool_fraction_with_verified_attribution": None,
                               "note": "Topic membership is not a buyer-specific spend denominator."},
        "pool_research_queue": result_pools, "sequence": phases,
        "limitations": ["Research hypotheses are not canonical edges",
                        "No verified supplier shares or capacity in this role map",
                        "Sector topics cannot establish specific buyer budgets"]
    }

def compare_reports(previous, current):
    """Read-only dependency delta; never schedules or mutates other workers."""
    require(isinstance(previous, dict) and previous.get("schema") == "basket.b19-maturation-audit@research1", "previous report is incompatible")
    require(isinstance(current, dict) and current.get("schema") == previous["schema"], "current report is incompatible")
    for label, report in (("previous", previous), ("current", current)):
        rows = report.get("pool_research_queue")
        require(isinstance(rows, list), f"{label}: missing pool research list")
        ids = [x.get("pool_id") for x in rows if isinstance(x, dict)]
        require(len(ids) == len(rows) and all(isinstance(i, str) and i for i in ids)
                and len(set(ids)) == len(ids), f"{label}: malformed or duplicate pool IDs")
        require(isinstance(report.get("input_fingerprint"), str)
                and re.fullmatch(r"[0-9a-f]{64}", report["input_fingerprint"]) is not None,
                f"{label}: invalid input fingerprint")
        require(isinstance(report.get("inputs"), dict) and isinstance(report.get("scope"), dict),
                f"{label}: missing source revision/scope")
    old = {x["pool_id"]: x for x in previous.get("pool_research_queue", [])}
    new = {x["pool_id"]: x for x in current.get("pool_research_queue", [])}
    affected = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
    return {"input_fingerprint_changed": previous.get("input_fingerprint") != current.get("input_fingerprint"),
            "upstream_revision_changed": previous.get("inputs") != current.get("inputs"),
            "scope_changed": previous.get("scope") != current.get("scope"),
            "changed_pool_ids": affected,
            "requires_reconciliation": previous.get("input_fingerprint") != current.get("input_fingerprint") or bool(affected)}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mapping", type=Path)
    parser.add_argument("pools", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--previous", type=Path, help="Prior report for deterministic read-only invalidation hints")
    args = parser.parse_args(argv)
    try:
        result = assess(json.loads(args.mapping.read_text(encoding="utf-8")),
                        json.loads(args.pools.read_text(encoding="utf-8")))
        if args.previous:
            previous = json.loads(args.previous.read_text(encoding="utf-8"))
            result["invalidation"] = compare_reports(previous, result)
        output = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0
    except (MaturityError, OSError, ValueError, TypeError, KeyError) as exc:
        print(f"MATURATION AUDIT FAIL: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
