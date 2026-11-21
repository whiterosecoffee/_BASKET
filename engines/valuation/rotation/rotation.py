"""Price-only, USD rotation scenarios. Run: python rotation.py input.json"""
import json
import sys
from datetime import date, datetime
from decimal import Decimal as D, ROUND_CEILING


def number(value):
    result = D(str(value))
    if not result.is_finite():
        raise ValueError("finite numbers required")
    return result


def instant(value):
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("timezone required")
    return result


def ceiling(value, unit="1"):
    return value.quantize(D(unit), rounding=ROUND_CEILING)


def analyze(data):
    h = data["held"]
    n = number(data["shares"])
    edge = number(data["terminal_edge"])
    sell, buy = map(number, data["cost_per_share"])
    if n <= 0 or n != int(n) or min(edge, sell, buy) < 0:
        raise ValueError("invalid shares, hurdle or costs")
    previous, current = data["paired_quotes"]
    elapsed = number((instant(current["at"]) - instant(previous["at"])).total_seconds()) / 60
    if elapsed <= 0:
        raise ValueError("quotes must be in chronological order")
    output = {}
    for c, cases in data["alternatives"].items():
        if c == h:
            raise ValueError("candidate equals holding")
        bid0, ask0, bid, ask = [number(q[key][ticker]) for q in (previous, current)
                                for key, ticker in (("bid", h), ("ask", c))]
        if min(bid0, ask0, bid, ask) <= 0 or bid <= sell:
            raise ValueError("invalid quote or sale cost")
        ratio = bid / ask
        movement = ratio / (bid0 / ask0)
        spend = n * (bid - sell)
        qty = int(spend // (ask + buy))
        rows = []
        for case in cases:
            years = case["years"]
            if years not in (1, 2, 3) or not case["source"] or instant(case["available_at"]) > instant(current["at"]):
                raise ValueError("invalid horizon, source or look-ahead")
            if date.fromisoformat(case["end"]) <= instant(current["at"]).date():
                raise ValueError("forward end date required")
            eh, mh, ec, mc = map(number, case["eps_multiple_held_then_candidate"])
            row = dict(case=case["name"], years=years, end=case["end"],
                       held_forward_pe=bid/eh if eh>0 else None,
                       candidate_forward_pe=ask/ec if ec>0 else None)
            if min(eh, mh, ec, mc) > 0:
                vh, vc = eh*mh, ec*mc
                needed = ceiling(n*vh*(1+edge)/vc)
                required = ceiling(sell + needed*(ask+buy)/n, ".01")
                row.update(held_value=vh, candidate_value=vc, required_shares=needed,
                           required_bid=required, bid_gap=required-bid, clears=bid>=required)
            else:
                row["status"] = "P/E scenario unavailable"
            rows.append(row)
        output[c] = dict(held_move_pct=100*(bid/bid0-1), candidate_move_pct=100*(ask/ask0-1),
                         quote_ratio=ratio, ratio_move_pct=100*(movement-1),
                         relative_log_bps_per_min=10000*movement.ln()/elapsed,
                         gross_usd=n*bid, whole_shares=qty, scenarios=rows)
    return output


if __name__ == "__main__":
    with open(sys.argv[1]) as source:
        print(json.dumps(analyze(json.load(source)), default=str, indent=2))
