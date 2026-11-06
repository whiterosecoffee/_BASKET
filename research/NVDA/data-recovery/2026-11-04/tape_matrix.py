"""Read a BASKET one-day Massive minute journal and emit the bar-only tape matrix."""
import argparse
import hashlib
import json
import math
from datetime import datetime, time, timedelta
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
MINUTE = timedelta(minutes=1)
FIVE = 5 * MINUTE
METHOD = "nvda.tape_matrix.research@1"
NOISE_BP = 5


def read_day(path, as_of):
    payload = path.read_bytes()
    bars = {}
    day = None
    for line in payload.splitlines():
        record = json.loads(line)
        value = record["value"]
        if (record["entity_id"], record["kind"], record["source"],
            value["interval"], value["adjustment_basis"]) != (
                "NVDA", "market_bar", "Massive", "1m", "unadjusted"):
            raise ValueError("Expected NVDA Massive unadjusted one-minute bars")
        minute = datetime.fromisoformat(record["observed_at"]).astimezone(ET)
        if minute.second or minute.microsecond:
            raise ValueError("Unaligned minute")
        if day is not None and day != minute.date():
            raise ValueError("Expected one exchange date per file")
        day = minute.date()
        available = max(datetime.fromisoformat(record[key])
                        for key in ("available_at", "ingested_at"))
        if available > as_of or minute + MINUTE > as_of:
            continue
        o, c, v = (float(value[key]) for key in ("open", "close", "volume"))
        if not all(map(math.isfinite, (o, c, v))) or min(o, c) <= 0 or v < 0:
            raise ValueError("Invalid price or volume")
        previous = bars.get(minute)
        if previous and record["record_id"] == previous[4]:
            continue
        if previous and (record.get("supersedes") != previous[4] or available < previous[3]):
            raise ValueError("Broken revision chain")
        bars[minute] = (o, c, v, available, record["record_id"])
    if day is None:
        raise ValueError("Empty journal")
    return day, bars, hashlib.sha256(payload).hexdigest()


def window(bars, start):
    rows = [bars.get(start + i * MINUTE) for i in range(5)]
    prior = bars.get(start - MINUTE)
    if any(row is None for row in rows) or (prior is None and start.time() != time(9, 30)):
        return None
    opening = rows[0][0] if start.time() == time(9, 30) else prior[1]
    closes = [opening] + [row[1] for row in rows]
    shares = sum(row[2] for row in rows)
    if shares <= 0:
        return None
    change = closes[-1] - opening
    path = sum(abs(b - a) for a, b in zip(closes, closes[1:]))
    near_flat = abs(change) < opening * NOISE_BP / 10_000
    auction_slot = start.time() in (time(9, 30), time(15, 55))
    return dict(start=start.isoformat(), close=closes[-1], shares=shares, change=change,
                usd_per_minute=change / 5, usd_per_million_shares=change * 1e6 / shares,
                shares_per_usd=None if near_flat else shares / abs(change),
                path_coherence=abs(change) / path if path else None,
                near_flat=near_flat, auction_slot=auction_slot)


def evaluate(journal, history, as_of):
    day, bars, digest = read_day(journal, as_of)
    baselines = {}
    for path in history:
        prior, data, sha = read_day(path, as_of)
        if prior >= day or prior in baselines:
            raise ValueError("Baseline journals must be distinct earlier sessions")
        baselines[prior] = (data, sha)
    start = datetime.combine(day, time(9, 30), ET)
    end = min(datetime.combine(day, time(16), ET), as_of)
    windows = []
    gaps = []
    for i in range(max(0, (end - start) // FIVE)):
        slot = start + i * FIVE
        row = window(bars, slot)
        if row is None:
            gaps.append(slot.isoformat())
            continue
        samples = []
        for prior in sorted(baselines, reverse=True):
            comp = window(baselines[prior][0], datetime.combine(prior, slot.time(), ET))
            if comp is not None:
                samples.append(comp["shares"])
            if len(samples) == 20:
                break
        row["baseline_count"] = len(samples)
        row["relative_volume"] = row["shares"] / median(samples) if len(samples) == 20 else None
        windows.append(row)
    # Pair the latest completed slot only. Never substitute a stale slot after a gap.
    paired = None
    if windows and datetime.fromisoformat(windows[-1]["start"]) + 2 * FIVE > end:
        current = windows[-1]
        current_start = datetime.fromisoformat(current["start"])
        if not current["near_flat"] and not current["auction_slot"]:
            for other in reversed(windows[:-1]):
                if current_start - datetime.fromisoformat(other["start"]) > 6 * FIVE:
                    break
                if not other["near_flat"] and not other["auction_slot"] and current["change"] * other["change"] < 0:
                    up, down = (current, other) if current["change"] > 0 else (other, current)
                    up_cost, down_cost = up["shares_per_usd"], down["shares_per_usd"]
                    paired = dict(up_start=up["start"], down_start=down["start"],
                                  up_shares_per_usd=up_cost, down_shares_per_usd=down_cost,
                                  easier="up" if up_cost < down_cost else
                                  "down" if down_cost < up_cost else "equal")
                    break
    return dict(method=METHOD, evidence="bar_only", as_of=as_of.isoformat(), session_date=day.isoformat(),
                input_sha256=digest, baseline_sha256={d.isoformat(): baselines[d][1] for d in sorted(baselines)},
                noise_floor_bp=NOISE_BP, windows=windows, missing_slots=gaps, latest_pair=paired)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("journal", type=Path)
    parser.add_argument("--as-of", required=True, type=datetime.fromisoformat)
    parser.add_argument("--history", nargs="*", type=Path, default=[])
    args = parser.parse_args()
    if args.as_of.utcoffset() is None:
        parser.error("--as-of must include a timezone")
    print(json.dumps(evaluate(args.journal, args.history, args.as_of), indent=2, allow_nan=False))
