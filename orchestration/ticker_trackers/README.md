# Evolving ORCL tracker

B00 composition component for #75. This is a runnable evidence ledger and HTML
snapshot renderer, not a deployed live trading terminal. Domain-owned adapters
and analytics remain integration dependencies. No current quotes or unverified
financial figures are bundled. The user-reported $124.40 low has no explicit
session date in the supplied request and is therefore not seeded as a current level.

## Run

From repository root, with Python 3.10+ (standard library only):

```sh
python -m orchestration.ticker_trackers.tracker --db /durable/data/orcl.sqlite init
python -m orchestration.ticker_trackers.tracker --db /durable/data/orcl.sqlite ingest /data/panel.json
python -m orchestration.ticker_trackers.tracker --db /durable/data/orcl.sqlite snapshot
python -m orchestration.ticker_trackers.tracker --db /durable/data/orcl.sqlite html > /data/orcl.html
python -m orchestration.ticker_trackers.tracker --db /durable/data/orcl.sqlite refresh
python -m orchestration.ticker_trackers.tracker --db /durable/data/orcl.sqlite history --as-of 2026-10-26T14:00:00Z
python -m unittest orchestration.ticker_trackers.test_tracker -v
```

The DB parent directory must exist. Use a durable location outside Git, protect
it with host permissions, and back up with SQLite's online backup API. The DB has
WAL, FULL synchronous durability, atomic inserts, duplicate detection, and SQL
UPDATE/DELETE prevention. These are accidental mutation safeguards, not a defense
against a host administrator replacing the DB. Renderer output is static: refresh
by ingesting new revisions and rendering again. No external scripts or telemetry.

## What evolves

`orcl.json` defines eight panels: price/dollar volume; narrow traversal bands and
regime; peer divergence; weighted macro baseline; revenue/margins/cash; financing
and capacity economics; partnership monetization; catalysts and thesis falsifiers.
Each panel has an owner, required research metrics, an operational freshness cap,
and a method contract. Metric lists are adapter acceptance requirements, not a
universal financial payload schema: each domain must validate its own payload.
An envelope's `verification` is the producer's assertion, not independent
verification by this orchestration component.

Every new observation appends a revision. A correction references `supersedes`;
old evidence remains retrievable. Correct a correction by referencing its successor.
Refresh output routes missing/stale/invalid panels to their owners in priority order.
Panel changes compare the latest observation to the previous known observation;
these are field changes, not a causal attribution or trade recommendation.

The baseline is an explicitly **unfitted heuristic prior**: credit 40%, rates 20%,
energy/inflation 25%, execution 15%. Freeze the baseline source IDs/time, preserve
raw units (bps, percentage points, USD), then let the B17 adapter standardize against
lagged-window changes with a declared sign convention. Missing factors suppress a
score. No automatic reweighting, probabilities or unsupported dollar price impacts.

## Input envelope

One JSON object per ingestion, exact top-level fields:

```json
{
  "schema": "basket.ticker_panel@1",
  "ticker": "ORCL",
  "panel": "market",
  "effective_at": "2026-10-26T14:00:00Z",
  "observed_at": "2026-10-26T14:00:00Z",
  "available_at": "2026-10-26T14:00:00Z",
  "expires_at": "2026-10-26T14:02:00Z",
  "classification": "source_fact",
  "verification": "unverified",
  "sources": [{"url":"https://example.com/synthetic", "label":"SYNTHETIC EXAMPLE ONLY"}],
  "data": {"last_usd":100, "session":"regular", "feed_delay_seconds":0},
  "method_version": "synthetic-example-1",
  "supersedes": null,
  "input_revisions": []
}
```

This example is deliberately unverified and not real ORCL data. No synthetic sample
can produce an eligible current signal without a caller changing its assertion.
Sources must be HTTPS. An actual adapter must supply authentic source provenance.
Use `source_fact`, `issuer_statement`, `derived`, `hypothesis` or `scenario`;
verification is `verified`, `unverified` or `disputed`. Hypotheses and scenarios
never become current signals even if their existence is verified.

Ingestion assigns `ingested_at` and content-addressed `revision_id`; caller-supplied
values are rejected. Identical content is idempotent. Dependencies must already
exist and have been available by output availability. Pass every dependent panel's
revision ID in `input_revisions`; adapters cannot omit dependencies to evade TTD.
Corrections to an input invalidate descendants until recomputed with new IDs.

## Time and freshness

- Effective: trade/event/period time. Observed: source observation or explicit review
  time. Available: source's first publication time. Ingested: this system's receipt.
- Replay uses BOTH source availability and ingestion time. Backfilled data cannot
  appear in a snapshot of what this tracker knew before ingestion.
- Expiry is the earlier of producer expiry and the panel's configured age cap.
  Equality is expired. Current data is null for expired/unverified/disputed inputs.
- A stale correction cannot revive a superseded original. Dependencies recursively
  enforce freshness and corrections. Future effective events may appear in catalysts;
  future effective values elsewhere cannot be current.
- Quarterly financial facts retain their historical truth. Revalidating the latest
  filing produces a new daily review revision with original fiscal effective date
  and source availability, not a forged new fiscal observation.
- Caps are conservative defaults, not session-aware scheduling or feed entitlements.
  A closed market will become stale; a future B02/B08 adapter must expose session state.
- This model is panel-granular. Per-series freshness and exact price-band trade
  aggregation belong to domain adapters. The composition layer does not calculate
  or independently verify bands, regressions or accounting metrics.

## Operational integration

Dependency #76 routes exact paths and acceptance to B02/B03/B04/B05/B06/B17/B08/B01.
B00 must arbitrate ORCL company ownership before company research files are added.
Existing continuous ingestion requests #61/#62 remain upstream; no duplicate feed
worker is created here. Feed producers should ingest prerequisite revisions, emit
validated dependent panels, then atomically publish a newly rendered snapshot.

Suggested deployment cadence (not an active schedule): market/traversal/divergence
on entitled regular-session updates; macro hourly with source-specific release
calendars; filings/partnerships on new evidence plus daily revalidation. B08 owns
persistent worker supervision, backups and authenticated serving. GitHub/chat is
not the data plane. No notifications, trades or background process are enabled by
running `init` or rendering HTML.
