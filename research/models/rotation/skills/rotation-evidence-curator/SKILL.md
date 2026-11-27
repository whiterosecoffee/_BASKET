---
name: rotation-evidence-curator
description: Collects and classifies news, guidance, consensus and industry forecasts that explain price moves or change EPS, with provenance and evidence class. Use when checking why a stock dropped or rebounded, logging an earnings or guidance event, or mapping industry forecasts (capex, memory pricing) to a stock's growth path.
compatibility: Firecrawl search/scrape, Massive news and treasury endpoints; no Benzinga or Quartr Pro entitlements.
metadata:
  owner: B04
  version: 1.0.0
---
# Evidence curator

## Evidence classes (state one per fact)
verified fact (filing, press release), issuer claim, secondary report, assumption, scenario output.

## Procedure
1. Prefer primary sources (press releases, 10-Q, call transcripts); headline-sourced items are secondary and unverified (gate V8).
2. Append to `guidance.csv`, `estimates.csv`, `multiple_events.csv`, `industry.csv`, `NEWS_<yyyy-mm>.md` with URL, date, class.
3. Rate and macro effects: log the yield move with `macro/treasury_yields.csv`; shave estimate is equity duration ~ 1/FCF yield.
4. Mark whether an event changed E (then it is an EPS update, handled in `rotation-valuation-tiers`).

## Stop rules
No claim without a source and date; no fabricated consensus.

## Hands off to
`rotation-valuation-tiers`, `rotation-data-steward`.
