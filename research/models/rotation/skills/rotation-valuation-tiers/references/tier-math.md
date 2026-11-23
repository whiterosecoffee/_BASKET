# Tier math
```
tier_bounds(m_lo, m_hi, n=5): r = (m_hi/m_lo)**(1/n); bounds = [m_lo * r**k for k in 0..n]
band_k(E) = E * [bounds[k], bounds[k+1]]
band_shift_pct = E_new / E_old - 1
tier_before/after = tier(price / E_old), tier(price / E_new)
```
Regression anchors: NVDA multiples 13.4 to 48.1 on E 9.31; the 2026-11-17 update (+18%) moved the unchanged price from tier 2 to tier 1. Code: `engines/valuation/rotation/bands.py`, `models.py`.
