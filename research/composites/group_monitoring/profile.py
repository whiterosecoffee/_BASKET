"""Pure research-ledger projection, not a canonical observation writer or scheduler."""
import hashlib
import json
import math
from datetime import datetime

VERSION = "0.1.0"
KEY = ("security", "metric", "period_end", "duration", "basis", "currency", "unit", "provider")


def instant(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timezone required")
    return result


def identity(row):
    return tuple(row[k] for k in KEY)


def merge(existing, incoming):
    """Validate a union; exact duplicates are no-ops. Never mutate caller inputs."""
    by_id = {}
    for row in [*existing, *incoming]:
        identity(row)
        instant(row["observed_at"])
        if not row.get("source_url", "").startswith("https://"):
            raise ValueError("HTTPS source required")
        value = row["value"]
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)):
            raise ValueError("finite numeric value or explicit null required")
        if value is None and not row.get("missing_reason"):
            raise ValueError("null needs missing reason")
        if row["id"] in by_id and by_id[row["id"]] != row:
            raise ValueError("immutable ID collision")
        by_id[row["id"]] = row
    ordered = sorted(by_id.values(), key=lambda x: (instant(x["observed_at"]), x["id"]))
    current = {}
    accepted = {}
    for row in ordered:
        key = identity(row)
        parent = row.get("supersedes")
        if parent:
            prior = accepted.get(parent)
            if prior is None or identity(prior) != key or current.get(key) != parent:
                raise ValueError("correction must supersede current matching record")
            if instant(row["observed_at"]) <= instant(prior["observed_at"]):
                raise ValueError("correction must be observed later")
        elif key in current:
            raise ValueError("same fact requires explicit correction")
        current[key] = row["id"]
        accepted[row["id"]] = row
    return ordered


def snapshot(records, as_of):
    """Replay what this ledger knew, using observation time, not publication date."""
    ordered = merge([], records)
    latest = {}
    for row in ordered:
        if instant(row["observed_at"]) <= instant(as_of):
            latest[identity(row)] = row
    rows = sorted(latest.values(), key=lambda x: x["id"])
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {"method_version": VERSION, "as_of": as_of, "input_sha256": hashlib.sha256(raw.encode()).hexdigest(), "records": rows}


def delta(prior, current, mode="revision"):
    """Explicit same-period revision or same-quarter YoY; never infer peer comparability."""
    for field in ("security", "metric", "duration", "basis", "currency", "unit", "provider"):
        if prior[field] != current[field]:
            raise ValueError("incomparable " + field)
    if mode == "revision":
        if prior["period_end"] != current["period_end"]:
            raise ValueError("revision periods differ")
    elif mode == "yoy":
        p, c = prior["period_end"], current["period_end"]
        if p[4:] != c[4:] or int(c[:4]) - int(p[:4]) != 1:
            raise ValueError("not matched year-over-year periods")
    else:
        raise ValueError("unsupported comparison mode")
    a, b = prior["value"], current["value"]
    if a is None or b is None:
        return {"status": "unavailable", "absolute": None, "relative_pct": None}
    return {"status": "comparable", "absolute": b-a, "relative_pct": (b/a-1)*100 if a > 0 else None}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("ledger")
    p.add_argument("--as-of", required=True)
    a = p.parse_args()
    with open(a.ledger, encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    print(json.dumps(snapshot(rows, a.as_of), indent=2, allow_nan=False))
