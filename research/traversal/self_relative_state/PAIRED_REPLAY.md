# Paired B06 replay and reproducible mechanism check

Issue #154, draft PR #160. Research specification only.

## First paired test

Freeze #145 episode boundaries, labels, evaluation horizon and #109 range/turnover plus #145 efficiency inputs before evaluation. Explicitly bound #150 geometry to the intended session. Fit and score the same baseline twice on identical eligible events, adding only the five-session percentage change in SMA30 to the second model. This paired comparison supplies the traversal-only control missing from the descriptive M0–M5 ladder. Keep the same training procedure, dates, thresholds policy and alert coverage. Then test other candidates individually. Rank is a transformation of distance, so measure incremental value conditional on distance.

Score compression at observation time. Score continuation, failed stabilization and reversal from subsequent completed bars with frozen breach/reclaim order and horizon. Retain unresolved, censored and order-ambiguous events. Split by date across tickers, keep each battle episode together, purge training outcomes crossing the split and resample contiguous date blocks. Report per-class counts, precision, recall, false reversal confirmations, delay, exclusions and uncertainty at equal alert coverage. Previously inspected November 2–3 examples are exploratory. A null or negative result is sufficient to close the research question.

## Reproduce the synthetic check

Extract the Python block below and run with Python 3 (assertions enabled). No dependencies or historical data. Equal total turnover uses one unit of volume at each synthetic close. The fixture uses signed occupancy over ten sessions as an auxiliary persistence comparison, distinct from the contract’s consecutive-session run length. Percentile is the strict 252-prior-observation variant (452 completed closes for SMA200). Neither choice overrides the contract. Constant prehistory is deliberately artificial. Two reorderings yield identical 20-session range position and SMA30 distance, but SMA30 slope changes from +0.88% to −1.13%. A one-day jump from a flat history gives a top percentile ahead of either possible future. These checks establish information differences only.

```python
"""Run with Python 3. Synthetic mechanism tests only. No market data copied.
Input to features: ordered, contiguous, split-consistent completed session closes
as available at decision time. Caller validates session calendar and provenance.
"""
from statistics import mean
from math import isclose


def features(closes, n):
    if len(closes) < n:
        return dict(distance=None, slope=None, persistence=None, percentile=None)
    averages = [mean(closes[i-n:i]) for i in range(n, len(closes)+1)]
    distances = [price / avg - 1 for price, avg in zip(closes[n-1:], averages)]
    prior = distances[-253:-1]
    return dict(distance=distances[-1],
                slope=averages[-1]/averages[-6]-1 if len(averages)>=6 else None,
                persistence=mean((x>0)-(x<0) for x in distances[-10:])
                if len(distances)>=10 else None,
                percentile=mean((x<distances[-1])+0.5*(x==distances[-1])
                                for x in prior) if len(prior)==252 else None)


def run():
    # Reverse the ordering of the same 20 closes, retaining today's price.
    # Equal volume each day implies equal total traded notional in this fixture.
    path = [90+i for i in range(19)]
    a, b = path+[100], path[::-1]+[100]
    assert (min(a),max(a),sum(a)) == (min(b),max(b),sum(b))
    a, b = [100]*450+a, [100]*450+b
    for n in (10,30,200):
        x,y = features(a,n), features(b,n)
        print(n, x, y)
        assert (isclose(x['distance'],y['distance'])) == (n!=10)
    # A late jump alone creates a displacement with zero prior trending.
    assert features([100]*451+[110],200)['percentile']==1
    assert features([100]*451+[110],200)['persistence']==0.1
    # Both outcomes share exactly the same as-of features.
    for suffix in ([111,112],[99,98]):
        assert features(([100]*451+[110]+suffix)[:-2],200)==features([100]*451+[110],200)
    for n in (10,30,200):
        assert features([100]*(n+251),n)['percentile'] is None
        assert features([100]*(n+252),n)['percentile']==0.5


if __name__=='__main__':
    run()
```
