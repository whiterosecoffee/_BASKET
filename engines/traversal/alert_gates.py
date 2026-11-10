"""B06 descriptive alert gates; never a live feed or calibrated forecast.

All observations must come from B02-owned timestamped inputs in production.
This pure evaluator neither polls providers nor persists canonical prices.
"""
from datetime import datetime, timezone
from math import isfinite


def _utc(value):
    if not isinstance(value, str):
        raise ValueError("timestamp_required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone_required")
    return parsed.astimezone(timezone.utc)


def evaluate(snapshot, *, max_age_seconds=900, divergence_pp=5.0):
    """Return deterministic evidence-qualified triggers and suppression reasons.

    snapshot fields: as_of, observations (ticker -> {price, previous_close,
    observed_at, available_at, currency, source_id, quote_status}), optional
    tokyo_threshold ({previous, current, observed_at, available_at, source_id}),
    optional news ({material, available_at, source_id}).
    Price and previous_close are same-currency, same-listing values.
    """
    as_of = _utc(snapshot["as_of"])
    if max_age_seconds < 0 or divergence_pp <= 0:
        raise ValueError("invalid_policy")
    accepted, rejected = {}, {}
    for ticker, item in snapshot["observations"].items():
        try:
            observed = _utc(item["observed_at"])
            available = _utc(item["available_at"])
            age = (as_of - observed).total_seconds()
            if age < 0 or (as_of - available).total_seconds() < 0:
                raise ValueError("future_observation")
            if available < observed:
                raise ValueError("availability_before_observation")
            if age > max_age_seconds:
                raise ValueError("expired")
            if item.get("quote_status") not in ("live", "delayed", "previous_close"):
                raise ValueError("quote_status_unknown")
            if item["quote_status"] == "previous_close":
                raise ValueError("previous_close_not_intraday")
            if not item.get("source_id") or not item.get("currency"):
                raise ValueError("missing_provenance")
            price, prior = float(item["price"]), float(item["previous_close"])
            if not all(map(isfinite, (price, prior))) or price <= 0 or prior <= 0:
                raise ValueError("invalid_price")
            accepted[ticker] = {"change_pct": 100 * (price / prior - 1),
                                "source_id": item["source_id"], "observed_at": item["observed_at"],
                                "quote_status": item["quote_status"]}
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            rejected[ticker] = str(exc)
    triggers = []
    parent = accepted.get("SFTBY")
    if parent and abs(parent["change_pct"]) >= 3:
        triggers.append({"type": "daily_move", "ticker": "SFTBY",
                         "change_pct": round(parent["change_pct"], 4)})
    if parent:
        for peer in ("ARM", "PAYP"):
            if peer in accepted:
                gap = parent["change_pct"] - accepted[peer]["change_pct"]
                if abs(gap) >= divergence_pp:
                    triggers.append({"type": "relative_divergence", "peer": peer,
                                     "gap_pp": round(gap, 4),
                                     "provisional": True})
    threshold = snapshot.get("tokyo_threshold")
    if threshold:
        try:
            if _utc(threshold["available_at"]) > as_of:
                raise ValueError("future_threshold")
            if (as_of - _utc(threshold["observed_at"])).total_seconds() > max_age_seconds:
                raise ValueError("expired_threshold")
            if not threshold.get("source_id"):
                raise ValueError("missing_threshold_source")
            a, b = float(threshold["previous"]), float(threshold["current"])
            if not all(map(isfinite, (a, b))) or a <= 0 or b <= 0:
                raise ValueError("invalid_threshold")
            for level in (4800, 5000):
                if a < level <= b:
                    triggers.append({"type": "tokyo_reclaim", "level_jpy": level})
                elif a >= level > b:
                    triggers.append({"type": "tokyo_break", "level_jpy": level})
        except (KeyError, ValueError, TypeError) as exc:
            rejected["tokyo_threshold"] = str(exc)
    news = snapshot.get("news")
    if news and news.get("material"):
        try:
            if not news.get("source_id") or _utc(news["available_at"]) > as_of:
                raise ValueError("unavailable_news")
            triggers.append({"type": "material_news", "source_id": news["source_id"]})
        except (KeyError, TypeError, ValueError) as exc:
            rejected["news"] = str(exc)
    return {"status": "review" if triggers else "quiet", "triggers": triggers,
            "accepted": accepted, "rejected": rejected,
            "warning": "descriptive_only_not_probability_or_live_feed"}
