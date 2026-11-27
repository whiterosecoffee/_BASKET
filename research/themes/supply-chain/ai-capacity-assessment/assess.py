"""Replay a 100%-utilization inference ownership scenario. JSON on stdin/stdout."""
import json
import math
import sys


def assess(case):
    result = []
    if not isinstance(case["systems"], list) or not case["systems"]:
        raise ValueError("systems must be a nonempty list")
    for s in case["systems"]:
        def number(key, minimum=0, positive=False):
            value = s[key]
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(key)
            if value < minimum or (positive and value == 0):
                raise ValueError(key)
            return value

        for key in ("system", "benchmark_source", "cost_source", "power_source", "workload"):
            if not isinstance(s[key], str) or not s[key].strip():
                raise ValueError(key)
        rate = number("output_tokens_s", positive=True)
        watts = 1000 * number("it_kw", positive=True)
        kwh = watts * number("pue", minimum=1) / (3.6 * rate)
        capital = number("price_usd")
        annual = capital * (1 / number("life_years", positive=True) + number("annual_opex_fraction"))
        cost = annual * 1e6 / (8760 * 3600 * rate) + kwh * number("usd_kwh")
        result.append({"system": s["system"], "it_tokens_per_joule": rate / watts,
                       "facility_kwh_per_million": kwh, "usd_per_million_output": cost})
    return {"version": 1, "as_of": case["as_of"], "utilization": 1,
            "status": "modeled_scenario", "systems": result}


if __name__ == "__main__":
    try:
        print(json.dumps(assess(json.load(sys.stdin)), allow_nan=False))
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        sys.exit(f"Invalid scenario: {error}")
