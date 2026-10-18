#!/usr/bin/env python3
"""Deterministic B13 evidence fingerprint and downstream invalidation proposal.

Read-only research adapter. No canonical store, scheduler, live price, trading
signal, or NAV. Inputs have DATE precision; no intraday replay is asserted.
"""
import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCHEMA = "basket.b13_evidence_fingerprint@1"
ENGINE_VERSION = "B13-evidence-fingerprint@0.1.0"
FACTOR_IDS = frozenset(("revenue_quality", "growth_durability", "unit_economics",
                        "capital_funding", "competitive_position",
                        "governance_dilution", "market_price_discovery",
                        "compute_delivery"))
ECONOMIC_FACTORS = frozenset(("revenue_quality", "growth_durability",
                              "unit_economics", "capital_funding",
                              "compute_delivery", "competitive_position"))


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def day(value):
    require(isinstance(value, str) and len(value) == 10,
            "date-only YYYY-MM-DD required; intraday availability unverified")
    return date.fromisoformat(value)


def records_of(rows, prefix, as_of, source_ids=None):
    """Preserve immutable ids; superseding revisions remain in the historical set."""
    keyed = {}
    for item in rows:
        identity = item.get("id")
        require(isinstance(identity, str) and identity,
                prefix + ": missing stable ID")
        require(identity not in keyed, prefix + ": duplicate id " + identity)
        observed = item.get("observation_on", item.get("available_on"))
        available = item.get("available_on")
        require(day(observed) <= day(available) <= day(as_of),
                prefix + ": unavailable or future date for " + identity)
        if source_ids is not None:
            require(bool(item.get("source_ids")) and
                    set(item["source_ids"]).issubset(source_ids),
                    prefix + ": unknown upstream source for " + identity)
        require(item.get("status") or item.get("verification_state"),
                prefix + ": missing evidence state " + identity)
        if prefix == "valuation":
            require(item.get("source_class") and item.get("unit") and
                    isinstance(item.get("value"), (int, float)),
                    prefix + ": missing class/unit/value " + identity)
        if prefix == "news":
            require(item.get("evidence_class") and item.get("temporal_precision") == "date_only",
                    prefix + ": news evidence missing class/date precision " + identity)
        keyed[identity] = item
    superseded = set()
    for key, item in keyed.items():
        ancestor = item.get("supersedes")
        if ancestor is not None:
            require(ancestor != key and ancestor in keyed,
                    prefix + ": unknown/cyclic revision parent " + key)
            require(day(keyed[ancestor]["available_on"]) <= day(item["available_on"]),
                    prefix + ": revision precedes original " + key)
            require(ancestor not in superseded,
                    prefix + ": competing revisions need explicit adjudication")
            superseded.add(ancestor)
    for identity in keyed:
        path, cursor = set(), identity
        while cursor is not None:
            require(cursor not in path,
                    prefix + ": revision cycle detected at " + identity)
            path.add(cursor)
            cursor = keyed[cursor].get("supersedes")
    return keyed, superseded


def build(as_of="2026-10-17", *, valuation=None, news=None,
          policy=None, resources=None):
    valuation = valuation if valuation is not None else load("valuation-register.json")
    news = news if news is not None else load("ipo2027-news.json")
    policy = policy if policy is not None else load("ipo2027-policy.json")
    resources = resources if resources is not None else load("resource-registry.json")

    require(valuation.get("schema") == "basket.preipo_valuation_research@1",
            "valuation source contract mismatch")
    require(news.get("schema") == "basket.openai_ipo_news@1",
            "news contract mismatch")
    require(policy.get("schema") == "basket.openai_ipo_weight_policy@1",
            "policy contract mismatch")
    require(resources.get("schema") == "basket.openai_source_registry@1",
            "resource registry contract mismatch")
    require(all(x.get("entity_id") == "OPENAI" for x in (valuation, news, policy, resources)),
            "unexpected entity")
    require(valuation["reporting_currency"] == policy["currency"] ==
            resources["reporting_currency"] == "USD", "USD reporting required")

    # Policy/entitlement records are static as-of research, NOT historical
    # market-available facts. Never pretend to replay them before their creation.
    vdate = day(valuation["as_of_date"])
    ndate = day(news["as_of_date"])
    pdate = day(policy["as_of_date"])
    rdate = day(resources["prepared_on"])
    requested = day(as_of)
    require(requested == vdate == ndate == pdate == rdate,
            "static date-vintage mismatch; retrieve a new verified research snapshot")

    source_table = valuation.get("sources", {})
    require(bool(source_table), "valuation source registry empty")
    for name, item in source_table.items():
        require(isinstance(name, str) and item.get("url", "").startswith("https://"),
                "invalid valuation source reference")
    val_rows, val_superseded = records_of(
        valuation["observations"], "valuation", as_of, set(source_table))
    news_rows, news_superseded = records_of(news["items"], "news", as_of)
    require(set(news_rows) == set(news["research_ids"]),
            "news index must equal row IDs")
    for row in news_rows.values():
        require(row.get("source_url", "").startswith("https://"),
                "news item lacks provenance")
        require(set(row["factor_ids"]).issubset(FACTOR_IDS),
                "unknown news factor")

    require(set(policy["factors"]) == FACTOR_IDS, "incompatible factor registry")
    for stage in policy["stages"].values():
        weight = stage["base_weights_pct"]
        require(set(weight) == FACTOR_IDS and sum(weight.values()) == 100
                and all(isinstance(w, (int, float)) and w > 0 for w in weight.values()),
                "IPO stage weights inconsistent")
    source_rows = {}
    for item in resources["sources"]:
        identity = item["id"]
        require(identity not in source_rows, "duplicate provider ID")
        require(item.get("url", "").startswith("https://"),
                "provider missing URL")
        require(set(item["factors"]).issubset(FACTOR_IDS),
                "provider references unknown factor")
        source_rows[identity] = item

    # Each record hash includes its upstream source definition. A correction of
    # a source URL invalidates affected claims, without mutating canonical facts.
    fingerprints, consumers, kinds = {}, {}, {}
    def add(key, payload, recipients, kind):
        require(key not in fingerprints, "duplicate fingerprint key")
        fingerprints[key] = sha(payload)
        consumers[key] = sorted(set(recipients))
        kinds[key] = kind

    for key, row in val_rows.items():
        consumers_for_row = ["B13"]
        metric = row["measurement"]
        if "perp" in metric:
            consumers_for_row += ["B21"]
        else:
            consumers_for_row += ["B04"]
        if metric.startswith("softbank_"):
            consumers_for_row += ["B09"]
        if key not in val_superseded:
            add("valuation:" + key,
                {"item": row, "sources": {s:source_table[s] for s in row["source_ids"]}},
                consumers_for_row, "valuation")
        else:
            add("valuation:" + key,
                {"item": row, "sources": {s:source_table[s] for s in row["source_ids"]}},
                ["B13"], "valuation_archived")
    for key, row in news_rows.items():
        recipients = ["B13", "B21"]
        if set(row["factor_ids"]) & ECONOMIC_FACTORS:
            recipients.append("B04")
        if key in news_superseded:
            recipients = ["B13"]
        add("news:" + key, row, recipients,
            "news_archived" if key in news_superseded else "news")
    add("policy:ipo2027", policy, ["B13"], "research_policy")
    for key, item in source_rows.items():
        # Entitlement/readiness changes do NOT directly revalue OpenAI.
        add("provider:" + key, item, ["B13", item["owner"]], "provider_readiness")

    consumer_inputs = {}
    for record_id, owners in consumers.items():
        for owner in owners:
            consumer_inputs.setdefault(owner, {})[record_id] = fingerprints[record_id]
    consumer_digests = {owner: sha(rows) for owner, rows in sorted(consumer_inputs.items())}
    result = {
        "schema": SCHEMA, "engine_version": ENGINE_VERSION,
        "as_of_date": as_of, "temporal_precision": "calendar_day",
        "reporting_currency": "USD", "entity_id": "OPENAI",
        "record_hashes": dict(sorted(fingerprints.items())),
        "record_kinds": dict(sorted(kinds.items())),
        "consumers_by_record": dict(sorted(consumers.items())),
        "consumer_input_hashes": consumer_digests,
        "research_vintages": {"valuation":valuation["as_of_date"],
                              "news":news["as_of_date"], "policy":policy["as_of_date"],
                              "source_registry":resources["prepared_on"]},
        "policy_version": policy["policy_version"],
        "source_registry_version": resources["version"],
        "source_state": "research_only_not_live",
        "valuation_state": "unknown_no_verified_equity_or_EV_model",
        "parent_nav_state": "unavailable",
        "first_available_precision": "date_only",
        "ingested_at_utc": None,
        "missing_source_timestamps": True,
        "data_snapshot_hash": None,
    }
    result["dependency_fingerprint"] = sha({
        "engine_version": ENGINE_VERSION, "as_of": as_of,
        "record_hashes": result["record_hashes"],
        "consumer_input_hashes": consumer_digests,
        "policy_version": result["policy_version"],
        "source_registry_version": result["source_registry_version"],
    })
    return result


def compare(previous, current):
    """Fail closed on silent record mutation and show precisely which consumers move."""
    require(previous["schema"] == current["schema"] == SCHEMA,
            "fingerprint contract mismatch")
    require(previous["entity_id"] == current["entity_id"] == "OPENAI",
            "mixed issuer comparison")
    require(previous["as_of_date"] == current["as_of_date"],
            "different snapshot vintage; explicit B02 revision mapping required")
    a, b = previous["record_hashes"], current["record_hashes"]
    deleted = sorted(set(a) - set(b))
    require(not deleted, "append-only input deletion: " + ", ".join(deleted))
    modified = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
    require(not any(k.startswith(("valuation:", "news:")) for k in modified),
            "in-place evidence mutation; append a new ID with supersedes")
    if previous["policy_version"] == current["policy_version"]:
        require("policy:ipo2027" not in modified,
                "policy changed without version increment")
    if previous["source_registry_version"] == current["source_registry_version"]:
        require(not any(k.startswith("provider:") for k in modified),
                "provider registry changed without version increment")
    added = sorted(set(b) - set(a))
    impacted = sorted(set(previous["consumer_input_hashes"]) |
                      set(current["consumer_input_hashes"]))
    changed = [x for x in impacted if
               previous["consumer_input_hashes"].get(x) !=
               current["consumer_input_hashes"].get(x)]
    return {"schema": "basket.b13_change_impact@1",
            "old_fingerprint": previous["dependency_fingerprint"],
            "new_fingerprint": current["dependency_fingerprint"],
            "is_idempotent": not added and not modified,
            "added_input_ids": added, "changed_input_ids": modified,
            "recompute_consumer_sparks": changed,
            "recompute_is_proposal_not_dispatched": True,
            "no_recompute_for_other_sparks": sorted(set(impacted) - set(changed))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", default="2026-10-17")
    parser.add_argument("--compare-json", help="prior fingerprint report from this research tool")
    args = parser.parse_args()
    current = build(args.as_of)
    if args.compare_json:
        before = json.loads(Path(args.compare_json).read_text(encoding="utf-8"))
        output = {"snapshot": current, "change_impact": compare(before, current)}
    else:
        output = current
    print(json.dumps(output, sort_keys=True, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit("B13 evidence fingerprint rejected: " + str(exc))
