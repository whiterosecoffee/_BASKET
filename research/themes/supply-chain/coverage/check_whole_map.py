#!/usr/bin/env python3
"""Validate B19 whole-basket research mapping against pinned upstream inputs."""
import argparse
import hashlib
import re
import json
import sys
from pathlib import Path

class MapError(ValueError):
    pass

def require(test, message):
    if not test:
        raise MapError(message)

def git_blob_sha(raw):
    """Git loose-blob SHA-1 over exact file bytes, not decoded JSON."""
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()

def verify_input_blobs(manifest_raw, pools_raw, manifest_blob, pool_blob):
    for label, raw, expected in (("manifest", manifest_raw, manifest_blob), ("pool", pools_raw, pool_blob)):
        require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{40}", expected) is not None,
                f"{label}: expected Git blob SHA-1 required")
        require(git_blob_sha(raw) == expected, f"{label}: input bytes do not match pinned Git blob")
    return True

def verify(mapping, manifest, pools, manifest_revision=None, pool_revision=None, strict_fingerprint=True):
    require(isinstance(mapping, dict) and mapping.get("schema") == "basket.b19-whole-basket-role-map@research1", "unsupported map")
    require(isinstance(manifest, dict) and isinstance(manifest.get("records"), list), "invalid instrument manifest")
    require(isinstance(pools, dict) and isinstance(pools.get("pools"), list), "invalid pool registry")
    rows = mapping.get("rows")
    require(isinstance(rows, list), "rows must be list")
    instruments = manifest["records"]
    pool_items = pools["pools"]
    symbols = [x.get("symbol") for x in instruments]
    row_ids = [x.get("symbol") for x in rows]
    pool_ids = [x.get("id") for x in pool_items]
    require(all(isinstance(s, str) and s for s in symbols + row_ids + pool_ids), "missing ID")
    require(len(set(symbols)) == len(symbols), "duplicate instrument")
    require(len(set(row_ids)) == len(row_ids), "duplicate map row")
    require(len(set(pool_ids)) == len(pool_ids), "duplicate pool")
    require(set(symbols) == set(row_ids), "map and manifest differ")
    source = {x["symbol"]: x for x in instruments}
    pool_set = set(pool_ids)
    grouped = dict.fromkeys(pool_ids, 0)
    eq_count = role_count = mapped_count = membership_count = 0
    for row in rows:
        sym = row["symbol"]
        require(row.get("instrument_type") == source[sym].get("instrument_type"), sym + ": instrument type mismatch")
        require(row.get("tracked_status") == source[sym].get("tracking_status"), sym + ": watchlist status mismatch")
        memberships = row.get("pool_ids")
        require(isinstance(memberships, list), sym + ": pool_ids invalid")
        require(len(set(memberships)) == len(memberships), sym + ": duplicate pool membership")
        require(all(p in pool_set for p in memberships), sym + ": unknown pool")
        equity = "equity" in row["instrument_type"] or "receipt" in row["instrument_type"]
        if equity:
            eq_count += 1
            require(bool(memberships or row.get("cross_cutting_roles")), sym + ": equity requires provisional role")
        else:
            require(not memberships and not row.get("cross_cutting_roles"), sym + ": nonissuer assigned issuer role")
        require(row.get("source_supported_revenue_usd") is None, sym + ": unsupported revenue")
        require(row.get("captured_share") is None, sym + ": unsupported share")
        require(row.get("production_capacity") is None, sym + ": unsupported capacity")
        require(row.get("contract_edges") == [], sym + ": unsupported contract promotion")
        require(row.get("evidence_refs") == [], sym + ": unsupported evidence promotion")
        require(row.get("canonical_entity_id") is None and row.get("venue_status") == "unverified", sym + ": identity promotion")
        if memberships or row.get("cross_cutting_roles"):
            role_count += 1
        if memberships:
            mapped_count += 1
        membership_count += len(memberships)
        for pool in memberships:
            grouped[pool] += 1
    stats = mapping.get("coverage", {})
    expected = {"all_tracked_instruments": len(rows), "classified_to_at_least_one_pool": mapped_count,
                "nonissuer_instruments": len(rows) - eq_count, "provisional_issuer_roles": eq_count,
                "unclassified_operating_issuers": 0, "unclassified_or_nonissuer": len(rows) - role_count,
                "operating_equity_with_pool_or_crosscutting_role": eq_count}
    for key, value in expected.items():
        require(stats.get(key) == value, key + ": stale summary")
    require(stats.get("pool_participant_counts") == grouped, "per-pool counts inconsistent")
    require(mapping.get("pool_reference", {}).get("pool_count") == len(pool_ids), "pool count mismatch")
    require(mapping.get("authoritative_scope", {}).get("count") == len(instruments), "scope count mismatch")
    if strict_fingerprint:
        require(isinstance(manifest_revision, str) and re.fullmatch(r"[0-9a-f]{40}", manifest_revision) is not None, "valid manifest revision required")
        require(isinstance(pool_revision, str) and re.fullmatch(r"[0-9a-f]{40}", pool_revision) is not None, "valid pool revision required")
        require(mapping.get("authoritative_scope", {}).get("head_sha") == manifest_revision, "manifest head fingerprint mismatch")
        require(mapping.get("pool_reference", {}).get("head_sha") == pool_revision, "pool head fingerprint mismatch")
    return {"all": len(rows), "equity_like": eq_count, "nonissuer": len(rows) - eq_count,
            "pool_assignments": membership_count, "provisional_role_coverage": role_count, "pools": len(pool_ids),
            "financial_coverage": "not measured"}

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mapping", type=Path)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("pools", type=Path)
    ap.add_argument("--manifest-revision", required=True, help="Pinned 40-character PR head SHA for the manifest")
    ap.add_argument("--pool-revision", required=True, help="Pinned 40-character PR head SHA for pool registry")
    ap.add_argument("--manifest-blob", help="Git blob SHA-1 of exact manifest bytes (must be paired with --pool-blob)")
    ap.add_argument("--pool-blob", help="Git blob SHA-1 of exact pool-registry bytes (must be paired with --manifest-blob)")
    a = ap.parse_args(argv)
    try:
        require(bool(a.manifest_blob) == bool(a.pool_blob), "both --manifest-blob and --pool-blob are required together")
        manifest_raw, pools_raw = a.manifest.read_bytes(), a.pools.read_bytes()
        if a.manifest_blob:
            verify_input_blobs(manifest_raw, pools_raw, a.manifest_blob, a.pool_blob)
        mapping = json.loads(a.mapping.read_text(encoding="utf-8"))
        manifest, pools = json.loads(manifest_raw), json.loads(pools_raw)
        result = verify(mapping, manifest, pools, a.manifest_revision, a.pool_revision)
        result["input_blobs_verified"] = bool(a.manifest_blob)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, TypeError, AttributeError, ValueError, KeyError) as exc:
        print("MAP FAIL: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
