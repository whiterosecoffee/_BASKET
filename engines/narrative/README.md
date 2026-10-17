# Narrative Intelligence Engine — v0.1

This module complements `runtime/ttd.py` and existing `tickers/*/history.jsonl`: it adds an **append-only evidence/perspective layer**, preserving competing hypotheses without promoting commentary into facts.

```bash
python engines/narrative/engine.py audit engines/narrative/cases/coreweave_2026-10-16.jsonl --at 2026-10-16T15:00:00Z
python engines/narrative/engine.py extrapolate engines/narrative/cases/coreweave_2026-10-16.jsonl --at 2026-10-16T15:00:00Z
python engines/narrative/engine.py sensitivity engines/narrative/cases/coreweave_2026-10-16.jsonl --at 2026-10-16T15:00:00Z --valuation-usd-b 1500 --move-pct -4
python -m unittest discover -s tests -p test_narrative.py
```

Requirements: Python >= 3.10, stdlib only. **No live quote provider, continuous scheduler or implied-data entitlements in this module.** The sample preserves reported claims and SEC primary facts. Data marked provisional may not silently become confirmed. Financial values use USD.

## Data contract

Each JSONL record: `id`, `kind` (fact, claim, hypothesis, perspective), `entity`, `metric`, `value`, `unit`, `observed_at` (measurement period or article observation), `available_at` (first public/available UTC), `ttd_seconds`, `source` with `url` and `tier`, `basis`, `status`, `dependencies`, `falsifiers`, `caveat`. Subject to immutable append-only revisions via new records with `supersedes`.

A source and methodology are mandatory for empirical claims. A **hypothesis is not a false claim** until a falsifying observation arrives; use supported, contradicted, or unresolved. Calculations include formula, upstream record IDs and as-of timestamp. Snapshot selection rejects look-ahead and dead inputs.

## Initial analytic checks

- Perp-implied valuation != private funding round / realized share price / discounted cash flow / public IPO pricing.
- Open interest != order-book depth, trading turnover or institutional valuation support.
- Bond YTM != contracted interest expense on fixed-rate debt.
- Contracted RPO != guaranteed cash/earnings, nor an annuity with no deployment, counterparty or margin risk.
- OpenAI and Anthropic net/gross revenue methodologies cannot be compared blindly.
- Parallel price declines are not evidence of CRWV → OpenAI causation; benchmark against the overall AI sector, oracle changes, funding, liquidity, timestamp ordering, credit spread and independent events.
- Disclosed CoreWeave customer shares do not establish OpenAI's percent or the allocation of its liabilities.
- Use genuine trading calendars, venue timestamps and quote TTD for market updates; all article quotes start as **reported claims**.

## Reference documentation

- CoreWeave 2026 Q2 10-Q (filed 2026-08-12): https://www.sec.gov/Archives/edgar/data/1769628/000176962826000366/crwv-20260630.htm
- HIP-3 oracle responsibility: https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals
- CNBC article, October 16 2026: original article titled "Here's how the CoreWeave sell-off is affecting OpenAI vs. Anthropic valuations" (exact URL pending independent verification)
- Reuters, October 15 2026: https://www.reuters.com/business/finance/investors-temper-anthropic-ipo-valuation-expectations-over-revenue-growth-2026-10-15/

Production adapters remain future work. See root `runtime/README.md` for TTD policy and disabled adapters.

## SoftBank exposure cross-check

SoftBank directly confirms ~13% OpenAI ownership and USD 64.6B cumulative funding as of 2026-10-01 (via Vision Fund 2). The `sensitivity` command requires an **explicit user/model-supplied hypothetical valuation**; it never imports a stale perp mark or publishes the result as official SoftBank NAV. https://group.softbank/en/news/press/20261001
