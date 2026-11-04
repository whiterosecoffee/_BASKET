"""B03-owned event ledger integrity checks. Run: python research/events/validate.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KINDS = {"earnings","guidance","partnership","contract","financing","acquisition","regime_change","other"}
STATUSES = {"hypothetical","announced","authorized","signed_framework","signed_definitive","funded","operational","completed","terminated"}
TICKERS = ("SFTBY", "CRWV", "AAOI", "NVDA")


def validate(canonical, revisions, schema):
    assert canonical["schema"] == schema["properties"]["schema"]["const"]
    assert set(canonical) <= set(schema["properties"]), "unknown top-level fields"
    assert all(k in canonical for k in schema["required"])
    assert revisions["entity_id"] == canonical["entity_id"]
    seen, rseen = set(), set()
    for event in canonical["events"]:
        assert all(k in event for k in schema["properties"]["events"]["items"]["required"])
        assert event["type"] in KINDS
        assert isinstance(event["sources"], list) and event["sources"]
        assert all(isinstance(s,str) and s.startswith("https://") for s in event["sources"])
        assert event["id"] not in seen, "duplicate event ID"
        assert event["available_at"] >= event["effective_at"] or event["metrics"].get("precision") == "date_only", "timestamp precision mismatch"
        seen.add(event["id"])
    for revision in revisions["events"]:
        assert revision["revision_id"] not in rseen, "duplicate revision ID"
        assert revision["event_id"] in seen
        assert revision["status"] in STATUSES
        assert revision["source_url"].startswith("https://")
        assert revision["supersedes"] is None or revision["supersedes"] in rseen, "unknown or forward supersedes"
        assert revision["available_at"], "first public availability must be captured"
        rseen.add(revision["revision_id"])
    assert all(any(r["event_id"] == e["id"] and r["source_url"] in e["sources"] for r in revisions["events"]) for e in canonical["events"])
    # Prevent ambiguous addition of already included final tranche and framework deal values.
    for event in canonical["events"]:
        m = event.get("metrics", {})
        if m.get("accounting_group") == "SFTBY-OpenAI-2026-followon":
            assert m["amount_usd"] <= m["cumulative_followon_usd"]
            assert m["incremental_usd"] == m["amount_usd"]
        if m.get("lifecycle") == "signed_framework":
            assert m.get("committed_capex_usd") is None
            assert m.get("contracted_revenue_usd") is None


def main():
    schema = json.loads((ROOT/"schemas/events.v1.json").read_text())
    checked = 0
    for ticker in TICKERS:
        path = ROOT/"tickers"/ticker/"events.json"
        if not path.exists():
            print(f"{ticker}: absent; not covered")
            continue
        canonical = json.loads(path.read_text())
        assert canonical["entity_id"] == ticker
        side = ROOT/"research/events"/ticker/"2026-10-16-initial-ledger.json"
        if side.exists():
            validate(canonical, json.loads(side.read_text()), schema)
        else:
            assert canonical["schema"] == "events@1"
            assert not canonical["events"], "populated ledger without audit revisions"
        checked += 1
    assert checked, "no canonical event ledgers"
    print(f"PASS: {checked} canonical ledgers; source/revision coverage checked where populated")


if __name__ == "__main__":
    main()
