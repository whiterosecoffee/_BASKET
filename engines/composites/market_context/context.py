"""Read-only, deterministic basket context. No network polling or trade execution."""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import sqlite3
import statistics
from datetime import datetime, timezone

VERSION = "1.0.0"
HERE = Path(__file__).resolve().parent


def stamp(value):
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("Timezone required")
    return t.astimezone(timezone.utc)


def number(value, positive=False):
    if isinstance(value, bool):
        raise ValueError("Boolean is not numeric")
    n = float(value)
    if not math.isfinite(n) or (positive and n <= 0):
        raise ValueError("Invalid finite/positive number")
    return n


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def change(price, baseline):
    return 100 * (number(price, True) / number(baseline, True) - 1)


def check_registry(registry):
    members = registry["members"]
    tickers = [m["ticker"] for m in members]
    if not tickers or len(tickers) != len(set(tickers)):
        raise ValueError("Empty/duplicate membership")
    for member in members:
        number(member.get("weight", 1), True)
        if member.get("currency", "USD") != "USD":
            raise ValueError("Requires USD input/verified upstream FX")
    return members


def normalize_massive(text, as_of, session, available_at=None, entitlement="unknown"):
    """Only adapters normalize provider fields; source session percentages are recomputed."""
    when = stamp(as_of)
    available_at = available_at or as_of
    if stamp(available_at) < when:
        raise ValueError("Availability precedes capture cutoff")
    quotes = {}
    for row in csv.DictReader(io.StringIO(text)):
        ticker = row["ticker"]
        if ticker in quotes:
            raise ValueError("Duplicate ticker")
        try:
            observed = datetime.fromtimestamp(int(row["session_last_updated"]) / 1e9, timezone.utc)
            if observed > when:
                raise ValueError("Future quote")
            q = {"price": number(row["session_price"], True),
                 "previous_close": number(row["session_previous_close"], True),
                 "observed_at": observed.isoformat(), "available_at": available_at,
                 "source": "Massive /v3/snapshot", "currency": "USD",
                 "entitlement": entitlement, "delay_seconds": 0,
                 "timestamp_kind": "provider_session_update", "session": session,
                 "baseline_id": "previous_close:" + when.strftime("%Y-%m-%d"),
                 "basis": "provider_snapshot_USD", "quality_flags": []}
            for source, target in [("session_open", "open"), ("session_vwap", "vwap"),
                                   ("session_high", "high"), ("session_low", "low"),
                                   ("session_volume", "volume")]:
                if row.get(source):
                    q[target] = number(row[source])
            if session == "premarket" and q.get("volume", 0) <= 0:
                q["quality_flags"].append("no_current_session_trades")
            minute = row.get("last_minute_last_updated")
            if minute:
                minute_at = datetime.fromtimestamp(int(minute) / 1e9, timezone.utc)
                q["last_trade_bar_at"] = minute_at.isoformat()
                # Detect reset/unchanged session_price inconsistent with a recent traded bar.
                if 0 <= (when-minute_at).total_seconds() <= 120 and row.get("last_minute_close"):
                    if abs(change(q["price"], row["last_minute_close"])) > 0.25:
                        q["quality_flags"].append("snapshot_bar_conflict")
        except (ValueError, TypeError, OverflowError) as exc:
            q = {"error": str(exc), "quality_flags": ["invalid_quote"]}
        quotes[ticker] = q
    snap = {"schema": "basket.market_context_input@1", "as_of": as_of,
            "available_at": available_at, "ingested_at": available_at,
            "session": session, "quotes": quotes, "macros": [],
            "supersedes": None, "availability_basis": "captured_response_bound"}
    snap["snapshot_id"] = digest(snap)
    return snap


def usable(q, snapshot, mode="strict"):
    if not q:
        return "missing"
    if q.get("quality_flags"):
        return "conflicting_or_invalid"
    try:
        number(q["price"], True)
        observed, available = stamp(q["observed_at"]), stamp(q["available_at"])
        cutoff = stamp(snapshot["as_of"])
        if observed > cutoff or available > stamp(snapshot["available_at"]):
            return "future"
        if available < observed:
            return "invalid_temporality"
        if q.get("currency") != "USD" or not q.get("source"):
            return "invalid_provenance"
        age = (cutoff-observed).total_seconds()
        if age > 120 + number(q.get("delay_seconds", 0)):
            return "stale"
        if q.get("last_trade_bar_at") and (cutoff-stamp(q["last_trade_bar_at"])).total_seconds() > 120 + number(q.get("delay_seconds", 0)):
            return "stale_trade_bar"
        if q.get("session") != snapshot["session"]:
            return "session_mismatch"
        if q.get("entitlement") not in ("realtime", "delayed"):
            return "provisional" if mode == "research" else "entitlement_unknown"
        if q.get("entitlement") == "delayed" and q.get("delay_seconds", 0) <= 0:
            return "delay_unknown"
        return "valid"
    except (ValueError, KeyError, TypeError):
        return "invalid"


def eligible(q, snapshot, mode):
    return usable(q, snapshot, mode) in ("valid", "provisional")


def pair(a, b, sa, sb, mode):
    if not eligible(a, sa, mode) or not eligible(b, sb, mode):
        return False
    return (a.get("basis") == b.get("basis") and a.get("currency") == b.get("currency")
            and abs((stamp(a["observed_at"])-stamp(b["observed_at"])).total_seconds()) <= 120)


def base_return(q):
    return change(q["price"], q["previous_close"]) if q.get("previous_close") else None


def relative(q, benchmark, snapshot, mode):
    if not pair(q, benchmark, snapshot, snapshot, mode):
        return None
    if q.get("baseline_id") != benchmark.get("baseline_id"):
        return None
    a, b = base_return(q), base_return(benchmark)
    return a-b if a is not None and b is not None else None


def comparison(current, previous, mode):
    """Cross-snapshot percent change. Pre/regular is allowed; same-clock volume is not inferred."""
    if not previous:
        return {}
    if stamp(previous["as_of"]) >= stamp(current["as_of"]):
        raise ValueError("Prior snapshot must precede current")
    if stamp(previous["available_at"]) > stamp(current["available_at"]):
        raise ValueError("Prior snapshot not known at current capture")
    out = {}
    for ticker, q in current["quotes"].items():
        p = previous["quotes"].get(ticker)
        if eligible(q, current, mode) and eligible(p, previous, mode):
            if q.get("basis") == p.get("basis"):
                out[ticker] = change(q["price"], p["price"])
    return out


def aggregate(rows, members, key, minimum=.75):
    weights = {m["ticker"]: number(m.get("weight", 1), True) for m in members}
    available = [r for r in rows if r.get(key) is not None]
    total = sum(weights.values())
    covered = sum(weights[r["ticker"]] for r in available)
    coverage = covered/total
    value = sum(weights[r["ticker"]]*r[key] for r in available)/covered if covered else None
    return {"coverage": coverage, "covered": len(available), "expected": len(members),
            "observed_subset_mean_pct": value,
            "basket_mean_pct": value if coverage >= minimum else None,
            "method": "configured_weight_mean_of_price_returns; not personal portfolio performance"}


def macro_score(policy, observations, as_of):
    """Policy bins + source/freshness gates. No probabilities; undefined inputs remain absent."""
    validate_policy(policy)
    by = {}
    for o in observations:
        if o["metric_id"] in by:
            raise ValueError("Duplicate macro metric")
        by[o["metric_id"]] = o
    scores, missing = {}, []
    for metric in policy["scoring_matrix"]:
        o = by.get(metric["id"])
        try:
            if not o or o.get("status") != "valid" or o.get("evidence_class") != "verified_observation":
                raise ValueError("Unverified")
            if not o.get("source") or not o.get("expires_at"):
                raise ValueError("Source/expiry required")
            if not (stamp(o["observed_at"]) <= stamp(o["available_at"]) <= stamp(as_of) <= stamp(o["expires_at"])):
                raise ValueError("Stale/future macro")
            x = number(o["value"])
            if o.get("unit") != metric["unit"]:
                raise ValueError("Unit mismatch")
            scores[metric["id"]] = metric["scores"][bisect.bisect_left(metric["thresholds"], x)]
        except (ValueError, KeyError, TypeError):
            missing.append(metric["id"])
    flags = []
    def value(mid):
        return number(by[mid]["value"]) if mid in scores else None
    def at_least(mid, limit):
        return value(mid) is not None and value(mid) >= limit
    if at_least("hy_oas", 600) or at_least("hy_oas_delta_5d", 75):
        flags.append("credit_stress")
    growth = (value("qqq_return_5d") is not None and value("qqq_return_5d") <= -4
              and at_least("hy_oas_delta_5d", 30) and value("nominal10y_delta_5d") is not None
              and value("nominal10y_delta_5d") <= -20)
    raw_scores = dict(scores)
    if growth:
        flags.append("growth_shock")
        for mid in ("real10y_delta_21d", "nominal10y_delta_5d", "breakeven5y_delta_21d", "wti_return_5d", "diesel_return_21d"):
            if mid in scores:
                scores[mid] = min(0, scores[mid])
    if at_least("wti_return_5d", 10) and at_least("breakeven5y_delta_21d", 20) and at_least("nominal10y_delta_5d", 20):
        flags.append("inflation_shock")
    pillars, coverage, effective = [], 0, 0
    for p in policy["pillars"]:
        mm = [m for m in policy["scoring_matrix"] if m["pillar"] == p["id"]]
        valid = [m for m in mm if m["id"] in scores]
        c = sum(m["within_pillar_weight"] for m in valid)
        v = 50+25*sum(m["within_pillar_weight"]*scores[m["id"]] for m in valid)/c if c >= .6 else None
        pillars.append({"pillar": p["id"], "weight": p["weight"], "coverage": c, "score": v})
        coverage += p["weight"]/100*c
        if v is not None:
            effective += p["weight"]/100
    publish = coverage >= .75 and effective >= .8 and all(next(p for p in pillars if p["pillar"] == x)["score"] is not None for x in ("credit", "rates"))
    value_out = sum(p["weight"]*p["score"] for p in pillars if p["score"] is not None)/(100*effective) if publish else None
    return {"score": value_out, "coverage": coverage, "effective_pillar_coverage": effective,
            "state": "scored" if publish else "insufficient_data", "pillars": pillars,
            "metric_scores": scores, "raw_metric_scores": raw_scores,
            "missing_metrics": missing, "stress_flags": flags,
            "calibration": "heuristic_unvalidated", "predictive_probability": None}


def validate_policy(policy):
    pillars = policy["pillars"]; metrics = policy["scoring_matrix"]
    if sum(p["weight"] for p in pillars) != 100 or len({p["id"] for p in pillars}) != len(pillars):
        raise ValueError("Invalid pillar weights/IDs")
    if len({m["id"] for m in metrics}) != len(metrics):
        raise ValueError("Duplicate metric IDs")
    for p in pillars:
        mm = [m for m in metrics if m["pillar"] == p["id"]]
        if not math.isclose(sum(number(m["within_pillar_weight"], True) for m in mm), 1):
            raise ValueError("Metric weights must sum to one")
    for m in metrics:
        if m["thresholds"] != sorted(set(m["thresholds"])) or len(m["thresholds"]) != 4 or len(m["scores"]) != 5:
            raise ValueError("Invalid bins")
        if any(s not in (-2,-1,0,1,2) for s in m["scores"]):
            raise ValueError("Invalid score")
        if m["pillar"] not in {p["id"] for p in pillars}:
            raise ValueError("Unknown pillar")


def macro_impulse(policy, current, previous):
    common = current["metric_scores"].keys() & previous["metric_scores"].keys()
    weights = {m["id"]: m["within_pillar_weight"]*next(p["weight"] for p in policy["pillars"] if p["id"] == m["pillar"])/100 for m in policy["scoring_matrix"]}
    coverage = sum(weights[x] for x in common)
    critical = all(sum(m["within_pillar_weight"] for m in policy["scoring_matrix"] if m["pillar"] == p and m["id"] in common) >= .6 for p in ("credit", "rates"))
    return {"score": 25*sum(weights[x]*(current["metric_scores"][x]-previous["metric_scores"][x]) for x in common)/coverage if coverage >= .75 and critical else None, "common_coverage": coverage, "horizon": "paired_snapshots; caller must certify a five-session calendar interval before labeling five-session impulse"}


def window_deltas(registry, current, history, minutes=(5,15,60), mode="strict"):
    members = check_registry(registry)
    result = {}
    for window in minutes:
        possible = [s for s in history if s["session"] == current["session"]
                    and stamp(s["available_at"]) <= stamp(current["available_at"])
                    and (stamp(current["as_of"])-stamp(s["as_of"])).total_seconds() >= window*60]
        prior = max(possible, key=lambda s:stamp(s["as_of"])) if possible else None
        elapsed = (stamp(current["as_of"])-stamp(prior["as_of"])).total_seconds() if prior else None
        if prior is None or elapsed-window*60 > 120:
            result[str(window)+"m"] = {"state":"missing_aligned_baseline", "basket_mean_pct":None}
            continue
        changes = comparison(current, prior, mode)
        rows = [{"ticker":m["ticker"],"change":changes.get(m["ticker"]) if m.get("quote_admission", "admitted") == "admitted" else None} for m in members]
        result[str(window)+"m"] = {**aggregate(rows,members,"change"),"elapsed_seconds":elapsed,"baseline_snapshot_id":prior["snapshot_id"]}
    return result


def analyze(registry, current, previous=None, mode="strict", policy=None, retrospective=False):
    members = check_registry(registry)
    stamp(current["as_of"])
    late_registry = stamp(registry["available_at"]) > stamp(current["available_at"]) or stamp(registry["effective_at"]) > stamp(current["as_of"])
    if late_registry and not retrospective:
        raise ValueError("Registry not available/effective at snapshot; explicit retrospective mode required")
    if stamp(current["available_at"]) < stamp(current["as_of"]) or stamp(current["ingested_at"]) < stamp(current["available_at"]):
        raise ValueError("Invalid capture chronology")
    changes = comparison(current, previous, mode)
    rows = []
    for m in members:
        t = m["ticker"]; q = current["quotes"].get(t)
        state = usable(q, current, mode) if m.get("quote_admission", "admitted") == "admitted" else "symbol_unverified"
        r = {"ticker": t, "group": m.get("group", "unmapped"), "sector_proxy": m.get("sector_proxy"),
             "status": state, "return_day_pct": None, "return_since_previous_pct": None,
             "relative_qqq_pp": None, "relative_sector_pp": None,
             "relative_qqq_since_previous_pp": None, "above_vwap_pct": None,
             "return_since_open_pct": None, "range_position": None}
        if state in ("valid", "provisional"):
            r.update(price_usd=q["price"], return_day_pct=base_return(q), return_since_previous_pct=changes.get(t),
                     relative_qqq_pp=relative(q, current["quotes"].get("QQQ"), current, mode),
                     relative_sector_pp=relative(q, current["quotes"].get(m.get("sector_proxy")), current, mode))
            if t in changes and "QQQ" in changes and previous:
                if pair(q, current["quotes"].get("QQQ"), current, current, mode) and pair(previous["quotes"].get(t), previous["quotes"].get("QQQ"), previous, previous, mode):
                    r["relative_qqq_since_previous_pp"] = changes[t]-changes["QQQ"]
            if current["session"] == "regular":
                for field, target in (("vwap", "above_vwap_pct"), ("open", "return_since_open_pct")):
                    if q.get(field) and q[field] > 0:
                        r[target] = change(q["price"], q[field])
                if q.get("high", 0) > q.get("low", 0) > 0:
                    r["range_position"] = (q["price"]-q["low"])/(q["high"]-q["low"])
            if "volume" in q and q["volume"] >= 0 and q.get("vwap",0) > 0:
                r["dollar_turnover_proxy_usd"] = q["volume"]*q["vwap"]
                r["dollar_turnover_method"] = "provider cumulative snapshot volume times VWAP; gross traded value proxy, not capital flow"
            d, rel = r["return_since_previous_pct"], r["relative_qqq_since_previous_pp"]
            r["state"] = "recovering_outperformer" if d is not None and d > 1 and rel is not None and rel > 1 else "weak_underperformer" if rel is not None and rel < -1 else "mixed"
        else:
            r["state"] = "unavailable"
        rows.append(r)
    available = [r for r in rows if r["return_day_pct"] is not None]
    valid_qqq = [r for r in rows if r["relative_qqq_pp"] is not None]
    daily = aggregate(rows, members, "return_day_pct")
    interval = aggregate(rows, members, "return_since_previous_pct")
    relative_basket = aggregate(rows, members, "relative_qqq_pp")
    relative_basket["unit"] = "percentage_points"  # generic aggregate field names retain compatibility
    groups = {}
    for g in sorted({r["group"] for r in rows}):
        gm = [m for m in members if m.get("group", "unmapped") == g]
        groups[g] = aggregate([r for r in rows if r["group"] == g], gm, "return_day_pct")
    if previous:
        interval["common_tickers"] = sorted(t for t in changes if t in {m["ticker"] for m in members})
        interval["note"] = "Same matched universe, direct price ratios; not difference of changing-basket averages."
    breadth = {"advancers": sum(r["return_day_pct"] > 0 for r in available),
               "decliners": sum(r["return_day_pct"] < 0 for r in available),
               "unchanged": sum(r["return_day_pct"] == 0 for r in available),
               "observed": len(available), "expected": len(members),
               "outperforming_qqq": sum(r["relative_qqq_pp"] > 0 for r in valid_qqq),
               "qqq_comparable": len(valid_qqq),
               "above_vwap": sum(r["above_vwap_pct"] is not None and r["above_vwap_pct"] > 0 for r in rows),
               "vwap_comparable": sum(r["above_vwap_pct"] is not None for r in rows),
               "dispersion_stddev_pp": statistics.pstdev(r["return_day_pct"] for r in available) if len(available) >= 2 else None}
    # Contribution denominator is fixed to configured membership, never just survivors.
    total_weight = sum(m.get("weight", 1) for m in members)
    weight_by = {m["ticker"]: m.get("weight", 1) for m in members}
    for r in available:
        r["observed_contribution_pp"] = r["return_day_pct"]*weight_by[r["ticker"]]/total_weight
    flags = []
    qqq = current["quotes"].get("QQQ")
    if eligible(qqq, current, mode):
        qret = base_return(qqq)
        if qret is not None and qret <= -1:
            flags.append("growth_index_down_at_least_1pct")
        for t in ("SPY", "IWM", "RSP"):
            rel = relative(current["quotes"].get(t), qqq, current, mode) if current["quotes"].get(t) else None
            if rel is not None and rel >= 1:
                flags.append(t.lower()+"_outperforming_qqq_by_1pp")
    macros = macro_score(policy, current.get("macros", []), current["as_of"]) if policy else None
    result = {"schema": "basket.market_context_report@1", "engine_version": VERSION,
              "as_of": current["as_of"], "snapshot_id": current["snapshot_id"],
              "previous_snapshot_id": previous["snapshot_id"] if previous else None,
              "registry_id": registry["registry_id"], "registry_hash": digest(registry),
              "registry_authority": registry["authority"], "mode": mode,
              "replay_class": "retrospective_diagnostic" if retrospective else "point_in_time",
              "quality": "provisional_research" if mode == "research" else "entitlement_checked",
              "daily": daily, "interval": interval, "relative_qqq": relative_basket, "participation": breadth,
              "groups": groups, "tickers": rows, "flags": flags, "macros": macros,
              "relative_leaders": sorted(valid_qqq,key=lambda r:r["relative_qqq_pp"],reverse=True)[:5],
              "relative_laggards": sorted(valid_qqq,key=lambda r:r["relative_qqq_pp"])[:5],
              "limitations": ["Relative returns are descriptive, not causal attribution or calibrated alpha.",
                              "Dollar trading volume is not net capital flow; no RVOL without matched-clock history.",
                              "Traversal/catalyst data remain external inputs; no probabilities or automatic orders."]}
    result["report_id"] = digest(result)
    return result


def refresh_plan(registry, snapshot=None, mode="strict"):
    members = check_registry(registry)
    targets = sorted({m["ticker"] for m in members if m.get("quote_admission", "admitted") == "admitted"} | set(registry.get("benchmarks", [])) | {m["sector_proxy"] for m in members if m.get("sector_proxy")})
    need = [t for t in targets if snapshot is None or not eligible(snapshot["quotes"].get(t), snapshot, mode)]
    return {"registry_id": registry["registry_id"], "expected_tickers": targets,
            "quote_batches": [need[i:i+100] for i in range(0, len(need), 100)],
            "quote_endpoint": "/v3/snapshot", "query_parameter": "ticker.any_of",
            "required_baselines": ["prior completed close", "previous snapshot", "regular-session open/VWAP", "5/21/63/200 completed-session history (B02/B06)"],
            "macro_sources": registry.get("macro_sources", {}),
            "unresolved_symbols": [m["ticker"] for m in members if m.get("quote_admission", "admitted") != "admitted"],
            "cadence_proposal": {"premarket_seconds": 300, "regular_seconds": 60, "afterhours_seconds": 300, "macro": "publication/event driven"},
            "execution": "Caller must provide exchange calendar, entitled producer, durable worker; this routine does not schedule or fetch."}


class Journal:
    """Consumer-local SQLite journal. B02 canonical observation stores stay untouched."""
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS snapshots (id TEXT PRIMARY KEY, content TEXT NOT NULL)")

    def append(self, snap):
        text = canonical(snap)
        if stamp(snap["available_at"]) < stamp(snap["as_of"]) or stamp(snap["ingested_at"]) < stamp(snap["available_at"]):
            raise ValueError("Invalid snapshot chronology")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO snapshots VALUES (?,?)", (snap["snapshot_id"], text))
            stored = self.db.execute("SELECT content FROM snapshots WHERE id=?", (snap["snapshot_id"],)).fetchone()[0]
            if stored != text:
                raise ValueError("Snapshot ID collision")
            if snap.get("supersedes"):
                old = self.db.execute("SELECT content FROM snapshots WHERE id=?", (snap["supersedes"],)).fetchone()
                if not old:
                    raise ValueError("Correction parent absent")
                parent = json.loads(old[0])
                if parent["as_of"] != snap["as_of"] or stamp(snap["available_at"]) <= stamp(parent["available_at"]):
                    raise ValueError("Correction must preserve capture time, arrive later")
                for row in self.db.execute("SELECT content FROM snapshots WHERE id!=?", (snap["snapshot_id"],)):
                    if json.loads(row[0]).get("supersedes") == snap["supersedes"]:
                        raise ValueError("Correction fork; supersede latest revision instead")
        return snap["snapshot_id"]

    def replay(self, as_of, known_at):
        candidates = [json.loads(r[0]) for r in self.db.execute("SELECT content FROM snapshots")]
        candidates = [s for s in candidates if stamp(s["as_of"]) <= stamp(as_of) and stamp(s["available_at"]) <= stamp(known_at) and stamp(s["ingested_at"]) <= stamp(known_at)]
        superseded = {s["supersedes"] for s in candidates if s.get("supersedes")}
        candidates = [s for s in candidates if s["snapshot_id"] not in superseded]
        return max(candidates, key=lambda s: (stamp(s["as_of"]), stamp(s["available_at"]), s["snapshot_id"])) if candidates else None


def read(path):
    return json.loads(Path(path).read_text())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan"); plan.add_argument("--registry", required=True)
    norm = sub.add_parser("normalize"); norm.add_argument("--csv", required=True); norm.add_argument("--as-of", required=True); norm.add_argument("--session", choices=["premarket", "regular", "afterhours"], required=True)
    report = sub.add_parser("report"); report.add_argument("--registry", required=True); report.add_argument("--current", required=True); report.add_argument("--previous"); report.add_argument("--mode", choices=["strict", "research"], default="strict"); report.add_argument("--policy", default=str(HERE/"policy.v1.json")); report.add_argument("--retrospective", action="store_true")
    append = sub.add_parser("append"); append.add_argument("--db", required=True); append.add_argument("--snapshot", required=True)
    replay = sub.add_parser("replay"); replay.add_argument("--db", required=True); replay.add_argument("--as-of", required=True); replay.add_argument("--known-at", required=True)
    args = p.parse_args()
    if args.command == "plan":
        out = refresh_plan(read(args.registry))
    elif args.command == "normalize":
        out = normalize_massive(Path(args.csv).read_text(), args.as_of, args.session)
    elif args.command == "report":
        out = analyze(read(args.registry), read(args.current), read(args.previous) if args.previous else None, args.mode, read(args.policy), args.retrospective)
    elif args.command == "append":
        out = {"snapshot_id": Journal(args.db).append(read(args.snapshot))}
    else:
        out = Journal(args.db).replay(args.as_of, args.known_at)
    print(json.dumps(out, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
