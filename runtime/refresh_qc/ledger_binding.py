"""Read-only evidence binding for existing FETCH artifacts, not a QC/promotion gate.

Paths are caller-supplied and never included in receipts. Hashes prove integrity
against caller-selected pins, not provider authenticity or historical execution.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

REQUIRED = frozenset({"plan", "done", "request_ledger", "apply_ledger", "capture", "output", "fetch_plan.py", "fetch_run.py", "verify_apply.py", "ticker_jsonl_tool.py"})
JSON_INPUTS = frozenset({"plan", "done", "request_ledger", "apply_ledger", "capture"})

class BindingError(ValueError):
    pass

def _reject_constant(value):
    raise BindingError("non_finite_json")

def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise BindingError("duplicate_json_key")
        result[key] = value
    return result

def _json(raw):
    try:
        return json.loads(raw, parse_float=Decimal, parse_constant=_reject_constant, object_pairs_hook=_pairs)
    except (ValueError, TypeError, UnicodeError) as exc:
        raise BindingError("invalid_json") from None

def _lines(raw):
    rows = [_json(line) for line in raw.splitlines() if line.strip()]
    if any(not isinstance(row, dict) for row in rows):
        raise BindingError("non_object_json_record")
    return rows

def _integer(value):
    return isinstance(value, int) and not isinstance(value, bool)

def bind_evidence(manifest):
    """Validate pinned artifacts. Never fetch, sanitize, apply, write or promote."""
    try:
        return _bind(manifest)
    except BindingError:
        raise
    except (OSError, KeyError, TypeError, ValueError, OverflowError, AttributeError):
        # Do not leak paths, raw values, or provider rows through an exception.
        raise BindingError("invalid_or_unreadable_artifact") from None

def _bind(manifest):
    artifacts = manifest["artifacts"]
    if set(artifacts) != REQUIRED:
        raise BindingError("artifact_set_mismatch")
    ticker, round_name = manifest["ticker"], manifest["round"]
    if not isinstance(ticker, str) or not re.fullmatch(r"[A-Z][A-Z0-9_.:-]{0,31}", ticker) or not isinstance(round_name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", round_name):
        raise BindingError("invalid_identity")
    raw, hashes = {}, {}
    for name in sorted(REQUIRED):
        record = artifacts[name]
        expected = record["sha256"]
        if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            raise BindingError("invalid_pin")
        path = Path(record["path"])
        with path.open("rb") as stream:
            before = path.stat()
            h = hashlib.sha256()
            chunks = []
            size = 0
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(chunk)
                size += len(chunk)
                if name in JSON_INPUTS:
                    if size > 32 * 1024 * 1024:
                        raise BindingError("json_artifact_too_large")
                    chunks.append(chunk)
            after = path.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino) or size != after.st_size:
            raise BindingError("artifact_changed_during_read")
        if h.hexdigest() != expected:
            raise BindingError("artifact_hash_mismatch:" + name)
        hashes[name] = expected
        if name in JSON_INPUTS:
            raw[name] = b"".join(chunks)
    plan = _json(raw["plan"])["plan"][ticker]
    done = _json(raw["done"])
    ranges = plan["ranges"]
    if len(ranges) != 1:
        raise BindingError("unsupported_multi_range_plan")
    start, end = ranges[0]["from"], ranges[0]["to"]
    if not isinstance(start, str) or not isinstance(end, str) or date.fromisoformat(start).isoformat() != start or date.fromisoformat(end).isoformat() != end or start > end:
        raise BindingError("invalid_range")
    requests = [r for r in _lines(raw["request_ledger"]) if r.get("ticker") == ticker and r.get("from") == start and r.get("to") == end]
    applies = [r for r in _lines(raw["apply_ledger"]) if r.get("ticker") == ticker and r.get("round") == round_name]
    if len(requests) != 1 or len(applies) != 1:
        raise BindingError("missing_or_ambiguous_ledger_match")
    request, applied = requests[0], applies[0]
    symbol = plan.get("symbol")
    if not isinstance(symbol, str) or not symbol or request.get("symbol") != symbol:
        raise BindingError("provider_symbol_mismatch")
    logged_at = request.get("at")
    if not isinstance(logged_at, str) or len(logged_at) > 40 or "T" not in logged_at:
        raise BindingError("invalid_request_timestamp")
    logged_time = datetime.fromisoformat(logged_at.replace("Z", "+00:00"))
    if logged_time.tzinfo is None:
        raise BindingError("invalid_request_timestamp")
    rows = _lines(raw["capture"])
    if not rows:
        raise BindingError("empty_capture")
    dates, timestamps = set(), set()
    fractional_volume_rows = 0
    for row in rows:
        t = row["t"]
        if not _integer(t) or t % 60000 or row.get("ticker") != ticker or row.get("class") != "bar" or row.get("grain") != "1min":
            raise BindingError("capture_identity_or_grain_mismatch")
        if t in timestamps:
            raise BindingError("duplicate_capture_timestamp")
        timestamps.add(t)
        day = datetime.fromtimestamp(t // 1000, timezone.utc).astimezone(ZoneInfo("America/New_York")).date().isoformat()
        if not start <= day <= end:
            raise BindingError("capture_outside_plan")
        dates.add(day)
        volume = row.get("vol")
        if not isinstance(volume, (int, Decimal)) or isinstance(volume, bool) or volume < 0:
            raise BindingError("invalid_volume")
        if isinstance(volume, Decimal):
            if abs(volume.adjusted()) > 308 or len(volume.as_tuple().digits) > 1000:
                raise BindingError("unsupported_volume_precision")
            fractional_volume_rows += volume != volume.to_integral_value()
    counts = (done.get("rows"), request.get("rows"), applied.get("staged_rows"))
    if any(not _integer(n) or n != len(rows) for n in counts):
        raise BindingError("row_count_mismatch")
    statuses = done.get("statuses")
    if done.get("ok") is not True or not isinstance(statuses, list) or len(statuses) != 1 or not _integer(statuses[0]) or statuses[0] != 200 or not _integer(request.get("status")) or request["status"] != 200 or not _integer(request.get("pages")) or request["pages"] < 1:
        raise BindingError("unsuccessful_fetch_evidence")
    if applied.get("applied") is not True or applied.get("status") != "applied" or applied.get("sha256_after") != hashes["output"]:
        raise BindingError("apply_output_binding_mismatch")
    needed = plan["needed"]
    if not isinstance(needed, list) or not needed or len(set(needed)) != len(needed) or set(needed) != set(plan["kind_by_session"]) or set(plan["kind_by_session"].values()) != {"missing"}:
        raise BindingError("unsupported_plan_kind")
    if not set(needed) <= dates:
        raise BindingError("missing_planned_session")
    return {
        "status": "correlated_legacy_evidence",
        "receipt_version": 1,
        "binder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "canonical_eligible": False,
        "ticker": ticker,
        "round": round_name,
        "artifact_sha256": hashes,
        "observed_capture_rows": len(rows),
        "observed_session_count": len(dates),
        "fractional_volume_rows": fractional_volume_rows,
        "request_logged_at": logged_time.isoformat(),
        "current_output_matches_recorded_post_apply_hash": True,
        "historical_capture_hash_bound": False,
        "historical_executed_code_bound": False,
        "historical_first_available_verified": False,
        "limitations": ["No provider authenticity or historical execution proof", "No OHLC quality, calendar completeness, entitlement or canonical promotion assessment", "Pins identify currently inspected bytes, not historical code", "Ledger range/count correlation does not authenticate capture bytes"],
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    try:
        manifest = _json(Path(args.manifest).read_bytes())
        receipt = bind_evidence(manifest)
    except (BindingError, OSError) as exc:
        print(json.dumps({"status": "blocked", "canonical_eligible": False, "reason": str(exc) if isinstance(exc, BindingError) else "manifest_unreadable"}))
        return 2
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
