"""B17 provisional virtual ETF portfolio policy.

Not a pricing feed, trading system, or validated forecasting model.
Fail closed on stale or unverified inputs. All dates ISO8601 UTC.
"""
from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite
from typing import Any

MODEL = 'basket.b17_virtual_etf_policy@0.1'
COMPONENT_WEIGHTS = {
    'forward_return': 0.35,
    'downside_risk': 0.20,
    'recurring_profit_capture': 0.20,
    'earnings_quality_and_fcf': 0.15,
    'diversification_and_liquidity': 0.10,
}


def _time(x: str) -> datetime:
    if not isinstance(x, str) or not x.endswith('Z'):
        raise ValueError('UTC Z timestamp required')
    return datetime.fromisoformat(x.replace('Z', '+00:00'))


def _number(x: Any) -> float:
    if isinstance(x, bool) or not isinstance(x, (float, int)) or not isfinite(x):
        raise ValueError('finite numeric score required')
    return float(x)


def allocate(snapshot: dict) -> dict:
    """Produce auditable capped long-only target weights; unallocated balance is CASH.

    Required row fields: ticker, segment, observed_at, available_at, expires_at,
    price_usd, eligible, scores. Scores are explicitly assumed normalized to 0..1;
    this routine does *not* infer or validate their predictive skill.
    """
    cutoff = _time(snapshot['cutoff'])
    if cutoff > datetime.now(timezone.utc):
        raise ValueError('future cutoff not supported in this research routine')
    max_name = _number(snapshot.get('max_name', 0.15))
    max_segment = _number(snapshot.get('max_segment', 0.35))
    if not 0 < max_name <= 1 or not 0 < max_segment <= 1:
        raise ValueError('invalid caps')
    candidates, rejected, seen = [], [], set()
    for r in snapshot.get('rows', []):
        ticker = r.get('ticker')
        if not isinstance(ticker, str) or not ticker or ticker in seen:
            raise ValueError('missing/duplicate ticker')
        seen.add(ticker)
        reason = None
        try:
            observed, available, expires = (_time(r[k]) for k in ('observed_at', 'available_at', 'expires_at'))
            if not observed <= available <= cutoff < expires:
                reason = 'not_point_in_time_valid'
            if r.get('eligible') is not True:
                reason = 'ineligible'
            if not isinstance(r.get('segment'), str) or not r['segment']:
                reason = 'missing_segment'
            if _number(r['price_usd']) <= 0:
                reason = 'invalid_price'
            scores = r['scores']
            if set(scores) != set(COMPONENT_WEIGHTS):
                reason = 'missing_score_component'
            else:
                values = [_number(scores[k]) for k in COMPONENT_WEIGHTS]
                if any(not 0 <= v <= 1 for v in values):
                    reason = 'invalid_score_range'
            if reason is None:
                strength = sum(COMPONENT_WEIGHTS[k] * scores[k] for k in COMPONENT_WEIGHTS)
                if strength <= 0:
                    reason = 'nonpositive_score'
        except (ValueError, KeyError, TypeError):
            reason = reason or 'invalid_or_missing_evidence'
        if reason:
            rejected.append({'ticker': ticker, 'reason': reason})
        else:
            candidates.append({'ticker': ticker, 'segment': r['segment'], 'strength': strength})

    # Capped proportional allocation: freeze capped names/segments and redistribute
    # to remaining names. If the portfolio lacks capacity, retain unallocated cash.
    candidates.sort(key=lambda r: r['ticker'])
    weights = {r['ticker']: 0.0 for r in candidates}
    segments = {r['ticker']: r['segment'] for r in candidates}
    strengths = {r['ticker']: r['strength'] for r in candidates}
    for _ in range(100):
        cash = max(0.0, 1.0 - sum(weights.values()))
        if cash < 1e-12:
            break
        open_names = [t for t in weights if weights[t] < max_name - 1e-12
                      and sum(weights[s] for s in weights if segments[s] == segments[t]) < max_segment - 1e-12]
        denom = sum(strengths[t] for t in open_names)
        if not denom:
            break
        increments = {t: cash * strengths[t] / denom for t in open_names}
        proposed = {t: min(max_name - weights[t], increments[t]) for t in open_names}
        # Proportionally clip each segment to remaining segment capacity.
        for seg in set(segments.values()):
            names = [t for t in open_names if segments[t] == seg]
            proposed_total = sum(proposed[t] for t in names)
            cap_left = max(0., max_segment - sum(weights[t] for t in weights if segments[t] == seg))
            if proposed_total > cap_left:
                factor = cap_left / proposed_total
                for t in names:
                    proposed[t] *= factor
        growth = sum(proposed.values())
        if growth < 1e-12:
            break
        for t, amount in proposed.items():
            weights[t] += amount
    return {
        'model': MODEL,
        'cutoff': snapshot['cutoff'],
        'weights': [{'ticker': t, 'weight': round(weights[t], 10),
                     'segment': segments[t], 'score': round(strengths[t], 8)}
                    for t in sorted(weights, key=lambda t: (-weights[t], t))],
        'cash_weight': round(max(0.0, 1.0 - sum(weights.values())), 10),
        'rejected': sorted(rejected, key=lambda x: x['ticker']),
        'warning': 'Research-only scores are not calibrated forecasts; no trading or backtest claims.'
    }
