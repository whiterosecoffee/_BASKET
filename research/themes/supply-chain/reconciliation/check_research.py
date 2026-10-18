#!/usr/bin/env python3
"""Fail-closed validation for B19 noncanonical research overlay (stdlib only)."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(rel):
    with (ROOT / rel).open(encoding="utf-8") as f:
        return json.load(f)

def validate(root=ROOT):
    errors = []
    def read(rel):
        try:
            with (root / rel).open(encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError) as exc:
            errors.append(f"{rel}: {exc}")
            return {}
    registry = read("registry/tickers.json")
    coverage = read("coverage/missing.json")
    pools = read("registry/pools.json")
    earnings = read("earnings/quarterly-intake.json")
    gateway = read("relationships/gateway-model.json")
    rules = read("reconciliation/rules.json")
    if registry.get("authority") != "research_only_noncanonical":
        errors.append("registry must declare noncanonical authority")
    if registry.get("canonical_entity_path") != "tickers/<entity_id>/entity.json":
        errors.append("registry must reference canonical ticker entity path")
    ids = [r.get("entity_id") for r in registry.get("tickers", []) if isinstance(r, dict)]
    if not ids or any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        errors.append("ticker IDs must be unique, nonempty strings")
    if set(ids) != set(coverage.get("earnings_unverified", [])):
        errors.append("missing coverage must match research ticker IDs")
    pool_ids = [p.get("id") for p in pools.get("pools", []) if isinstance(p, dict)]
    if not pool_ids or len(pool_ids) != len(set(pool_ids)):
        errors.append("economic pool IDs must be unique and nonempty")
    for p in pools.get("pools", []):
        if p.get("status") == "unmeasured" and p.get("quarterly_final_demand_usd") is not None:
            errors.append("unmeasured pool cannot claim demand")
    if earnings.get("authority") != "research_only_noncanonical" or earnings.get("canonical_owner") != "B03":
        errors.append("earnings proposals must defer to B03")
    if gateway.get("authority") != "research_only_noncanonical" or gateway.get("canonical_owner") != "B05":
        errors.append("gateway hypotheses must defer to B05")
    if earnings.get("proposals") or gateway.get("hypotheses"):
        errors.append("proposals require separate evidence-level review; this checker validates only empty scaffolds")
    if not isinstance(rules.get("principles"), list) or not rules["principles"]:
        errors.append("missing reconciliation principles")
    return errors

if __name__ == "__main__":
    issues = validate()
    for issue in issues:
        print("ERROR:", issue, file=sys.stderr)
    if issues:
        sys.exit(1)
    print("B19 overlay structure OK (NOT earnings, issuer, or canonical membership validation)")
