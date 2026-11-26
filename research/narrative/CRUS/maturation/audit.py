"""CRUS research-only readiness audit; no prices, forecasts, ingestion or network.

Local contract v1 is a proposed consumer check, not a new canonical schema.
Evidence classification is supplied by a reviewer; this does not verify truth.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

VERSION = "crus-readiness@0.1.1"
REQUIRED = ("product_role", "commercial_scale", "customer_concentration",
            "margin_bridge", "eps_fy2027", "eps_fy2028", "quote", "capital_structure")
KINDS = {"issuer_statement", "reported_financial", "third_party_claim", "unknown"}


def stamp(value):
    if not isinstance(value, str):
        raise ValueError("exact timestamp required")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timezone required")
    return result


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate(data):
    canonical(data)  # Reject NaN and infinity, even in unused fields.
    if not isinstance(data, dict):
        raise ValueError("snapshot object required")
    if data.get("contract") != "crus-research-snapshot@1" or data.get("ticker") != "CRUS":
        raise ValueError("wrong research contract or ticker")
    records = data.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("nonempty records required")
    seen = set()
    for r in records:
        if not isinstance(r, dict) or not isinstance(r.get("id"), str) or not r["id"]:
            raise ValueError("record ID required")
        if r["id"] in seen:
            raise ValueError("duplicate record ID")
        seen.add(r["id"])
        if r.get("kind") not in KINDS or r.get("metric") not in REQUIRED:
            raise ValueError("invalid kind or metric")
        if r.get("review") not in {"source_read", "pending", "conflicted"}:
            raise ValueError("invalid review state")
        for key in ("available_at", "observed_at", "ingested_at", "valid_until"):
            if key not in r:
                raise ValueError("missing timestamp field: " + key)
            if r[key] is not None:
                stamp(r[key])
        if r["kind"] == "unknown":
            if r.get("value") is not None or r["review"] != "pending":
                raise ValueError("unknown must remain null and pending")
        else:
            if r.get("value") is None:
                raise ValueError("known record requires a value")
            if not isinstance(r.get("source"), dict):
                raise ValueError("source required")
            url = r["source"].get("url")
            if not isinstance(url, str) or urlsplit(url).scheme != "https" or not urlsplit(url).hostname:
                raise ValueError("HTTPS source required")
            if r["source"].get("class") not in {"primary", "secondary"}:
                raise ValueError("source class required")
        if r.get("basis") not in {"historical", "current", "estimate"}:
            raise ValueError("basis required")
        if r["metric"].startswith("eps_") and r["kind"] != "unknown":
            if r.get("accounting_basis") not in {"GAAP", "non-GAAP"}:
                raise ValueError("EPS accounting basis required")
            if r.get("fiscal_year") != int(r["metric"][-4:]):
                raise ValueError("fiscal-year mismatch")
            if not isinstance(r.get("value"), (int, float)) or isinstance(r["value"], bool):
                raise ValueError("numeric EPS required")
            if r.get("currency") != "USD":
                raise ValueError("USD EPS required")
        if r["kind"] != "unknown":
            if r["metric"] == "quote":
                if not number(r["value"]) or r["value"] <= 0 or r.get("currency") != "USD":
                    raise ValueError("positive USD quote required")
                if r.get("session") not in {"regular", "premarket", "afterhours"} or not isinstance(r.get("venue"), str) or not r["venue"].strip():
                    raise ValueError("quote venue/session required")
            if r["metric"] == "customer_concentration":
                if not number(r["value"]) or not 0 <= r["value"] <= 1:
                    raise ValueError("concentration fraction required")
            if r["metric"] == "capital_structure":
                v = r["value"]
                if not isinstance(v, dict) or r.get("currency") != "USD":
                    raise ValueError("USD capital structure object required")
                if not all(number(v.get(k)) and v[k] >= 0 for k in ("cash_usd", "debt_usd", "diluted_shares")) or v["diluted_shares"] <= 0:
                    raise ValueError("cash, debt and positive diluted shares required")
        if all(r[k] is not None for k in ("observed_at", "ingested_at")):
            if stamp(r["ingested_at"]) < stamp(r["observed_at"]):
                raise ValueError("ingestion before observation")
        if all(r[k] is not None for k in ("available_at", "ingested_at")):
            if stamp(r["ingested_at"]) < stamp(r["available_at"]):
                raise ValueError("ingestion before availability")
        if all(r[k] is not None for k in ("observed_at", "valid_until")):
            if stamp(r["valid_until"]) <= stamp(r["observed_at"]):
                raise ValueError("invalid validity interval")
    hypotheses = data.get("hypotheses", [])
    if not isinstance(hypotheses, list):
        raise ValueError("hypotheses list required")
    for h in hypotheses:
        if not isinstance(h, dict):
            raise ValueError("hypothesis object required")
        if not h.get("alternatives") or not h.get("falsifiers") or not h.get("milestone"):
            raise ValueError("hypothesis requires alternative, milestone and falsifier")
        for key in ("alternatives", "falsifiers"):
            if not isinstance(h[key], list) or not all(isinstance(x, str) and x.strip() for x in h[key]):
                raise ValueError("nonempty text lists required")
        if not isinstance(h["milestone"], str) or not h["milestone"].strip():
            raise ValueError("milestone text required")
        if not isinstance(h.get("dependencies"), list) or not h["dependencies"] or not all(isinstance(x, str) for x in h["dependencies"]) or not set(h["dependencies"]) <= seen:
            raise ValueError("unresolved hypothesis dependencies")
    return data


def audit(data, as_of):
    validate(data)
    cutoff = stamp(as_of)
    output = []
    for r in data["records"]:
        flags = []
        if r["kind"] == "unknown":
            flags.append("missing")
        if r["review"] != "source_read":
            flags.append(r["review"])
        # A report can exist historically while being unusable for current valuation.
        times = [r[k] for k in ("available_at", "observed_at", "ingested_at")]
        if any(t is None for t in times):
            flags.append("unknown_point_in_time")
        elif any(stamp(t) > cutoff for t in times):
            flags.append("not_yet_known")
        if r["basis"] == "historical":
            flags.append("historical_only")
        if r["valid_until"] is None:
            flags.append("unknown_current_validity")
        elif cutoff >= stamp(r["valid_until"]):
            flags.append("expired")
        output.append({"id": r["id"], "metric": r["metric"], "flags": sorted(flags),
                       "eligible": not flags})
    metrics = {}
    for metric in REQUIRED:
        rows = [r for r in output if r["metric"] == metric]
        # Multiple observations of a required metric need owner reconciliation;
        # never select the most optimistic or silently choose a revision.
        metrics[metric] = "eligible" if len(rows) == 1 and rows[0]["eligible"] else "blocked"
    ready = all(v == "eligible" for v in metrics.values())
    return {"model_version": VERSION, "input_sha256": hashlib.sha256(canonical(data)).hexdigest(),
            "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "as_of": as_of, "status": "inputs_eligible_for_owner_review" if ready else "blocked",
            "metrics": metrics, "records": output,
            "valuation": None, "investment_score": None,
            "limitations": ["Eligibility is not verified economic truth or a valuation.",
                            "No source retrieval, canonical promotion, probabilities or trading output."]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("snapshot")
    p.add_argument("--as-of", required=True)
    args = p.parse_args()
    try:
        result = audit(json.loads(Path(args.snapshot).read_text()), args.as_of)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}))
        return 1
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["status"] == "inputs_eligible_for_owner_review" else 2


if __name__ == "__main__":
    raise SystemExit(main())
