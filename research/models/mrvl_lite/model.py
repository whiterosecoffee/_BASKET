"""Offline research arithmetic. Canonical ingestion and traversal remain upstream."""
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

VERSION = "0.1.0"


def number(value, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Expected a numeric input")
    if not math.isfinite(value) or (positive and value <= 0):
        raise ValueError("Expected a finite input in the permitted range")
    return value


def spread(acquirer, target, ratio):
    parity = number(acquirer, True) * number(ratio, True)
    return 1 - number(target, True) / parity


def paired_spread(acquirer, target, ratio):
    """Require identical aware timestamps and session labels, never join lows."""
    for quote in (acquirer, target):
        stamp = datetime.fromisoformat(quote["at"].replace("Z", "+00:00"))
        if stamp.utcoffset() is None:
            raise ValueError("Timestamp requires a timezone")
    if acquirer["at"] != target["at"] or acquirer["session"] != target["session"]:
        raise ValueError("Pair timestamps and sessions must match")
    return spread(acquirer["price"], target["price"], ratio)


def rebound(price, low_touch):
    return number(price, True) / number(low_touch, True) - 1


def pro_forma(acquirer_eps, target_eps, acquirer_shares, target_shares,
              ratio, savings, tax, costs):
    """Same-period adjusted EPS and fully diluted shares, USD and share units."""
    a = number(acquirer_shares, True)
    t = number(target_shares, True)
    r = number(ratio, True)
    if not 0 <= number(tax) <= 1:
        raise ValueError("Tax must be between zero and one")
    if number(savings) < 0 or number(costs) < 0:
        raise ValueError("Savings and costs must be nonnegative")
    shares = a + r * t
    income = number(acquirer_eps) * a + number(target_eps) * t
    return (income + (savings - costs) * (1 - tax)) / shares


def evaluate(case):
    """Suppress targets until source, period and transaction assumptions reconcile."""
    blockers = []
    for key in ("sources_verified", "standalone_estimates_verified",
                "diluted_shares_verified", "periods_aligned", "deal_terms_verified"):
        if case.get(key) is not True:
            blockers.append(key)
    if case.get("input_conflicts"):
        blockers.append("input_conflicts")
    encoded = json.dumps(case, sort_keys=True, allow_nan=False).encode()
    result = {"model_version": VERSION, "input_sha256": hashlib.sha256(encoded).hexdigest(),
              "status": "blocked" if blockers else "scenario_only", "blockers": blockers,
              "eps": None, "price": None}
    if blockers:
        return result
    if case["acquirer_period_end"] != case["target_period_end"]:
        raise ValueError("EPS periods must match")
    if case["basis"] != "adjusted" or case["currency"] != "USD":
        raise ValueError("This prototype requires adjusted USD inputs")
    inputs = case["inputs"]
    eps = pro_forma(**inputs)
    result.update(eps=eps, price=eps * number(case["multiple"], True))
    if eps <= 0:
        result.update(price=None, status="nonpositive_earnings")
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("case", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate(json.loads(args.case.read_text())), indent=2, allow_nan=False))
