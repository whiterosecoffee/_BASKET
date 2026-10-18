#!/usr/bin/env python3
"""B19 research-only overlay validation; no canonical promotion or source verification."""
import json
import pathlib
import re
import sys
from datetime import datetime
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
PERIOD = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def _timestamp(value):
    if not isinstance(value, str) or not ISO.fullmatch(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False

def _url(value):
    p = urlparse(value) if isinstance(value, str) else None
    return bool(p and p.scheme == "https" and p.netloc and "." in p.netloc)

def validate(root=ROOT):
    errors = []
    def read(path):
        try:
            with (root / path).open(encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, ValueError) as exc:
            errors.append(f"{path}: {exc}")
            return {}
    reg = read("registry/tickers.json")
    coverage = read("coverage/missing.json")
    pools = read("registry/pools.json")
    earnings = read("earnings/quarterly-intake.json")
    gateways = read("relationships/gateway-model.json")
    rules = read("reconciliation/rules.json")
    if reg.get("authority") != "research_only_noncanonical" or reg.get("canonical_entity_path") != "tickers/<entity_id>/entity.json":
        errors.append("research ticker list must defer to canonical entity records")
    ids = [r.get("entity_id") for r in reg.get("tickers", []) if isinstance(r, dict)]
    if not ids or any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        errors.append("research ticker IDs must be unique nonempty strings")
    if set(ids) != set(coverage.get("earnings_unverified", [])):
        errors.append("coverage must reconcile to research ticker IDs")
    pool_ids = [p.get("id") for p in pools.get("pools", []) if isinstance(p, dict)]
    if not pool_ids or any(not isinstance(i, str) or not i for i in pool_ids) or len(pool_ids) != len(set(pool_ids)):
        errors.append("pool IDs must be unique nonempty strings")
    for p in pools.get("pools", []):
        if p.get("status") == "unmeasured" and p.get("quarterly_final_demand_usd") is not None:
            errors.append("unmeasured pool cannot have measured demand")
    if earnings.get("authority") != "research_only_noncanonical" or earnings.get("canonical_owner") != "B03":
        errors.append("issuer observations must defer to B03")
    if gateways.get("authority") != "research_only_noncanonical" or gateways.get("canonical_owner") != "B05":
        errors.append("relationship proposals must defer to B05")
    if not isinstance(rules.get("principles"), list) or not rules.get("principles"):
        errors.append("missing reconciliation rules")
    seen = set()
    for idx, row in enumerate(earnings.get("proposals", [])):
        loc = f"earnings proposal {idx}"
        required = ("entity_id", "fiscal_period", "period_end", "published_at", "source_url", "metric", "value_usd", "classification", "available_at", "ingested_at", "revision_id")
        if not isinstance(row, dict) or any(k not in row for k in required):
            errors.append(f"{loc}: missing required fields")
            continue
        if row["entity_id"] not in ids:
            errors.append(f"{loc}: entity outside research coverage")
        if not PERIOD.fullmatch(str(row["period_end"])):
            errors.append(f"{loc}: invalid period_end")
        else:
            try:
                datetime.strptime(row["period_end"], "%Y-%m-%d")
            except ValueError:
                errors.append(f"{loc}: impossible period_end")
        if any(not _timestamp(row[k]) for k in ("published_at", "available_at", "ingested_at")):
            errors.append(f"{loc}: timestamps must be timezone-aware ISO8601")
        if not _url(row["source_url"]):
            errors.append(f"{loc}: missing HTTPS evidence URL")
        if row["classification"] not in ("issuer_reported", "issuer_guidance", "derived", "hypothesis"):
            errors.append(f"{loc}: invalid evidence classification")
        if not isinstance(row["value_usd"], (int, float)) or isinstance(row["value_usd"], bool) or not -1e15 < row["value_usd"] < 1e15:
            errors.append(f"{loc}: invalid USD value")
        if not isinstance(row["revision_id"], str) or not row["revision_id"]:
            errors.append(f"{loc}: missing revision ID")
        key = (row["entity_id"], row["fiscal_period"], row["metric"], row["revision_id"])
        if key in seen:
            errors.append(f"{loc}: duplicate revision")
        seen.add(key)
        if all(_timestamp(row[k]) for k in ("published_at", "available_at", "ingested_at")):
            times = [datetime.fromisoformat(row[k].replace("Z", "+00:00")) for k in ("published_at", "available_at", "ingested_at")]
            if times[1] < times[0] or times[2] < times[1]:
                errors.append(f"{loc}: impossible evidence chronology")
    for idx, edge in enumerate(gateways.get("hypotheses", [])):
        loc = f"gateway hypothesis {idx}"
        if not isinstance(edge, dict) or not all(k in edge for k in ("source_entity_id", "target_entity_id", "relationship_type", "classification", "source_url", "available_at", "revision_id")):
            errors.append(f"{loc}: missing required evidence")
            continue
        if edge["source_entity_id"] not in ids or edge["target_entity_id"] not in ids:
            errors.append(f"{loc}: unknown endpoint")
        if edge["classification"] not in ("hypothesis", "inference", "issuer_statement", "verified_observation"):
            errors.append(f"{loc}: invalid classification")
        if not _url(edge["source_url"]) or not _timestamp(edge["available_at"]) or not edge["revision_id"]:
            errors.append(f"{loc}: invalid provenance")
        if "flow_usd" in edge and edge["flow_usd"] is not None:
            errors.append(f"{loc}: monetary flow cannot be asserted from an unreviewed hypothesis")
    return errors

if __name__ == "__main__":
    problems = validate()
    for item in problems:
        print("ERROR:", item, file=sys.stderr)
    if problems:
        sys.exit(1)
    print("B19 overlay structure/evidence shape PASS; issuer truth and canonical membership NOT verified")
