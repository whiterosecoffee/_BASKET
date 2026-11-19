"""AH-MRI deterministic research report. No fetching, streaming, or quote entitlement."""
from datetime import datetime, time
from zoneinfo import ZoneInfo
from hashlib import sha256
import json
import math
from readiness import evaluate as evaluate_readiness

VERSION = "ah-mri-research-0.2"

def timestamp(s):
    if not isinstance(s, str):
        raise ValueError("ISO timestamp with offset required")
    try:
        t = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError("invalid timestamp") from e
    if t.tzinfo is None or t.utcoffset() is None:
        raise ValueError("timezone offset required")
    return t

def price(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
        raise ValueError("positive finite USD price required")
    return float(v)

def event_number(value):
    """Require a finite JSON number; never turn booleans or text into data."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("finite numeric economic value required")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError("finite numeric economic value required") from exc
    if not math.isfinite(result):
        raise ValueError("finite numeric economic value required")
    return result

def provenance(row, as_of):
    fields = ("observed_at", "available_at", "ingested_at", "expires_at")
    if any(row.get(f) is None for f in fields):
        return "unknown"
    o, a, i, e = (timestamp(row[k]) for k in fields)
    if o > as_of or a > as_of or i > as_of:
        return "future_or_unavailable"
    if not o <= a <= i or e < i:
        return "invalid"
    return "expired_historical" if e <= as_of else "eligible"

def analyze(payload):
    as_of = timestamp(payload["as_of"])
    s = payload["session"]
    if s.get("status") != "completed" or timestamp(s["rth_end_at"]) > as_of:
        raise ValueError("external calendar must establish completed RTH session")
    if not s.get("date") or not s.get("calendar_id"):
        raise ValueError("session metadata missing")
    market_tz = ZoneInfo("America/New_York")
    rth_end = timestamp(s["rth_end_at"])
    if rth_end.astimezone(market_tz).date().isoformat() != s["date"]:
        raise ValueError("session date and close timestamp disagree")
    ah_end = timestamp(s["ah_end_at"]) if s.get("ah_end_at") else datetime.combine(
        rth_end.astimezone(market_tz).date(), time(20, 0), market_tz
    )
    if ah_end <= rth_end:
        raise ValueError("invalid AH session cutoff")
    out = {"schema": "basket.ah_mri.result@0.2", "engine_version": VERSION,
           "as_of": payload["as_of"], "session_date": s["date"], "calendar_id": s["calendar_id"],
           "market_state": "unclassified", "instruments": [], "events": [],
           "scenarios": [], "unknowns": list(payload.get("unknowns", []))}
    seen = set()
    for row in payload.get("instruments", []):
        ticker = row["ticker"]
        if not isinstance(ticker, str) or not ticker or ticker in seen:
            raise ValueError("ticker missing or duplicated")
        seen.add(ticker)
        x = {"ticker": ticker, "rth_close_usd": None, "rth_return_pct": None,
             "rth_observed_at": None, "rth_source": None, "rth_freshness": "unavailable",
             "ah_mark_usd": None, "ah_observed_at": None, "ah_source": None,
             "ah_freshness": "unavailable", "levels": [], "gaps": []}
        r = row.get("rth")
        if r:
            st = provenance(r, as_of)
            if (st in ("eligible", "expired_historical") and r.get("session") == "RTH"
                    and r.get("currency") == "USD" and r.get("source")
                    and timestamp(r["observed_at"]) == rth_end):
                x["rth_close_usd"] = price(r["close_usd"])
                x["rth_source"] = r["source"]
                x["rth_observed_at"] = r["observed_at"]
                x["rth_freshness"] = st
                if r.get("previous_close_usd") is not None:
                    p = price(r["previous_close_usd"])
                    x["rth_return_pct"] = round(100 * (x["rth_close_usd"] / p - 1), 4)
                if st == "expired_historical":
                    x["gaps"].append("RTH historical/expired; not live")
            else:
                x["gaps"].append("RTH unavailable: " + st + " or session/source mismatch")
        else:
            x["gaps"].append("missing RTH")
        ah = row.get("ah")
        if ah is not None:
            st = provenance(ah, as_of)
            if (st == "eligible" and ah.get("session") == "AH"
                    and ah.get("kind") == "trade" and ah.get("source")
                    and ah.get("currency") == "USD"
                    and rth_end < timestamp(ah["observed_at"]) <= ah_end):
                x["ah_mark_usd"] = price(ah["price_usd"])
                x["ah_observed_at"] = ah["observed_at"]
                x["ah_source"] = ah["source"]
                x["ah_freshness"] = st
            else:
                x["gaps"].append("AH unavailable: " + st + " or session/type mismatch")
        for z in row.get("levels", []):
            low, high = price(z["lower_usd"]), price(z["upper_usd"])
            if high < low:
                raise ValueError("support interval reversed")
            kind = z.get("kind")
            if kind not in ("reference", "observed", "scenario"):
                raise ValueError("invalid level kind")
            ids = z.get("evidence_ids", [])
            if not isinstance(ids, list):
                raise ValueError("evidence ids must be a list")
            if kind == "observed":
                # Caller-provided IDs cannot independently certify observed support.
                kind = "reference"
                x["gaps"].append("observed level downgraded: no independent volume/price verification")
            x["levels"].append({"kind": kind, "lower_usd": low, "upper_usd": high,
                                "evidence_ids": ids, "calculation": z.get("calculation"),
                                "confirmation": z.get("confirmation"), "invalidation": z.get("invalidation")})
        out["instruments"].append(x)
        out["unknowns"].extend(ticker + ": " + gap for gap in x["gaps"])
    for event in payload.get("events", []):
        e = {"name": event["name"], "scheduled_at": event["scheduled_at"],
             "units": event.get("units"), "surprise": None, "status": "scheduled"}
        if event.get("actual") is not None:
            available = timestamp(event["actual_available_at"])
            consensus_at = timestamp(event["consensus_available_at"])
            actual_units = event.get("actual_units")
            consensus_units = event.get("consensus_units")
            same_units = (bool(event.get("units")) and
                          (actual_units is None or actual_units == event["units"]) and
                          (consensus_units is None or consensus_units == event["units"]))
            if (available <= as_of and consensus_at < available
                    and consensus_at <= as_of
                    and timestamp(event["scheduled_at"]) <= available
                    and same_units):
                actual, consensus = event_number(event["actual"]), event_number(event["consensus"])
                surprise = event_number(actual - consensus)
                e["surprise"] = round(surprise, 8)
                e["status"] = "reported"
            else:
                e["status"] = "unavailable_as_of"
        out["events"].append(e)
    for scenario in payload.get("scenarios", []):
        if scenario.get("name") not in ("absorption", "continuation", "dislocation"):
            raise ValueError("invalid scenario")
        out["scenarios"].append({"name": scenario["name"], "trigger": scenario.get("trigger"),
                                 "invalidation": scenario.get("invalidation"), "probability": None})
    out["readiness"] = evaluate_readiness(payload.get("readiness_evidence"))
    out["input_manifest_hash"] = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return out

def markdown(report):
    lines = ["# AH-MRI — " + report["session_date"],
             "As of " + report["as_of"] + " | " + report["market_state"] + " | research-only", "",
             "| Symbol | RTH close USD | RTH change | AH eligible trade | Battle bands |",
             "|---|---:|---:|---|---|"]
    for x in report["instruments"]:
        close = "unavailable" if x["rth_close_usd"] is None else "$%.2f" % x["rth_close_usd"]
        ret = "unavailable" if x["rth_return_pct"] is None else "%+.2f%%" % x["rth_return_pct"]
        ah = "unavailable" if x["ah_mark_usd"] is None else "$%.2f @ %s" % (x["ah_mark_usd"], x["ah_observed_at"])
        bands = "; ".join("%s $%.2f–$%.2f" % (z["kind"], z["lower_usd"], z["upper_usd"]) for z in x["levels"]) or "unavailable"
        lines.append("| %s | %s | %s | %s | %s |" % (x["ticker"], close, ret, ah, bands))
    lines.append("\n## Price provenance")
    for x in report["instruments"]:
        rth = ("%s @ %s (%s)" % (x["rth_source"], x["rth_observed_at"], x["rth_freshness"])
               if x["rth_source"] else "unavailable")
        ah = ("%s @ %s (%s)" % (x["ah_source"], x["ah_observed_at"], x["ah_freshness"])
              if x["ah_source"] else "unavailable")
        lines.append("- %s: RTH %s; AH %s" % (x["ticker"], rth, ah))
    state = report["readiness"]
    lines.append("\n## Validation readiness")
    lines.append("Research only; independent verified gates %d/%d, production ready: %s" %
                 (state["independently_verified_gates"], state["required_gates"], state["production_ready"]))
    lines.append("Missing or invalid: " + (", ".join(state["blockers"]) or "claimed inputs unverified"))
    lines.append("\n## Economic events")
    lines.extend("- %s: %s; surprise %s %s" % (e["name"], e["status"], e["surprise"] if e["surprise"] is not None else "unknown", e["units"] or "") for e in report["events"])
    lines.append("\n## Conditional scenarios (uncalibrated)")
    lines.extend("- %s: trigger %s; invalidation %s" % (s["name"], s["trigger"] or "unknown", s["invalidation"] or "unknown") for s in report["scenarios"])
    lines.append("\n## Evidence gaps")
    lines.extend("- " + u for u in report["unknowns"] or ["None additionally supplied"])
    lines.append("\nEngine %s | input SHA256 %s" % (report["engine_version"], report["input_manifest_hash"]))
    return "\n".join(lines) + "\n"

