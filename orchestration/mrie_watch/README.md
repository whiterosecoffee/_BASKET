# MRIE watch integration — B00 #180

This read-only adapter assembles existing work; it does not ingest filings, write
canonical evidence, deliver alerts, upload Library artifacts or run a scheduler.
Input/output is frozen JSON. `watch.reconcile` accepts the staged scope manifest,
real canonical entities, dispatcher coverage, source-scan receipts, B03 event
proposals and latest owner-accepted revision identities. It returns a deterministic
review (`basket.mrie_watch_review@1`), coverage gaps and B03/B05 routing proposals.
No queue/store/checkpoint is mutated. `notification_candidate` means only that the
supplied materiality/backfill flags permit owner review; `notify` remains false.

## Reuse and source identity

- #48 / PR49 dispatcher: commit `b63e917758b9eab1e40f01d72330262264fbbd90`,
  plan.py Git blob `65d9f00aa307739d33fd0737eb0ea8fa4d92a47c`.
  Load externally with `load_dispatcher`; missing/tampered dependency fails closed.
  No copy, new task allocator or worker launch.
- #146 / PR147 scope: commit `321c93c281aeeb7d63b5d107cca6a320070d5f02`,
  manifest blob `876c729bedeaebfeb867a51cde591118cf32aa75`. Provisional watchlist,
  not an approved security master. Funds need issuer review; index/FX/futures
  are explicitly excluded from issuer admission, never removed from scope audit.
- #12 / PR14 B03: commit `63f7cf68d2c3d72afe4b0beb841c03867289a51c`,
  validator blob `0089ff3da43f085e79b6909dc217b89e97786b33`.
  Its event statuses are reused; this adapter is a proposal envelope, not a
  replacement for canonical `schemas/events.v1.json` validation.
- #51 B05 graph, #132/PR133 evidence reducer, #134/PR135 Projects adapter,
  #148 canonical resolver/migration remain their existing owners' responsibilities.

## Readiness (2026-11-04; main b4910122a4c3f6ade747f2e4d59bd2d2e84b3c95)

| Required resource | State / evidence / owner |
|---|---|
| Registry and instrument resolver | Partial: 291 provisional instruments; 4 canonical entity files; #146/#148 B00 |
| CIK / foreign / ADR crosswalk | Missing full-universe verified mapping; B00 identity / B03 sources |
| SEC and issuer IR adapters | Partial source research, no verified continuous full-basket adapter; #12 B03 |
| Incremental discovery / PIT validation | Partial: frozen snapshot replay here, source discovery blocked B03 |
| Filing / economic-event dedup | Partial: owner-supplied stable IDs and accepted baseline here; identity/extraction B03 |
| Fact / claim / inference / scenario / unknown | Implemented proposal classification gate; canonical acceptance B03 |
| Immutable provenance / revisions | Partial: B03 ledger; this adapter emits revision proposals, never overwrites |
| Canonical issuer-event records | Partial: SFTBY ledger PR14 unmerged; B03 |
| Cross-basket economic relationships | Partial schema/sidecars, #51 graph pending; B05 |
| Gap planning / owner routing | Implemented PR49 pure compiler, unmerged; this adapter reuses pinned source |
| Schema / regression / CI | Existing B01 shared workflow; this branch tests separately; no integration claim |
| MRIE Library output | Blocked current access/readback unverified; historical reports aren't fresh proof |
| Materiality / notifications | Partial: proposal gate only, policy and actual delivery B03/B08 |
| Observability / replay / recovery | Partial: deterministic read-only replay here; hosted execution/persistence unverified B08 |

## Input boundary

Each proposal requires event_id, string revision, normalized economic content_hash
(SHA256), HTTPS source_url, available_at, published_at, effective_at, ingested_at,
classification, status, affected_tickers, boolean material and boolean backfill.
Timestamps require explicit zones; publication/effective times may be null.
Retain date-only/month-only source precision outside this envelope; never invent
midnight timestamps. Availability after as-of is quarantined. First availability
is not publication. An amendment alone does not create a new economic event.
B03 must assign event identities across accessions/documents/tickers and provide
source excerpts, units, reporting periods, original currency and dated B02 FX.
This adapter deliberately does not infer economics, convert currencies or claim
an HTTPS URL proves an official source. No USD or valuation outputs are generated.

`previous` is an explicit latest owner-accepted baseline, not all historical
revisions. Same payload is duplicate even with another document. Changed payload
requires a new revision; same revision changed hash is a conflict. All conflicting
same-cycle proposals remain non-actionable. Missing backfill classification is
review-required. Source failure/missing source identity remains incomplete.
Even all-success scan receipts mean snapshot_processed, not verified no news.

## Reproducible frozen replay

From repository root, with separately retrieved pinned dependency paths:

```sh
python -m orchestration.mrie_watch.replay --dispatcher /path/to/PR49/plan.py \
  --manifest /path/to/PR147/manifest.json --tickers tickers \
  --as-of 2026-11-04T06:00:00Z
python -m unittest orchestration.tests.test_mrie_watch
```

Observed full-scope run: 291 rows, 198 equity/ADR, 59 fund/ETP, 30 index,
3 futures, 1 FX. 254 identity reviews, 34 nonissuer exclusions, 3 canonical
identities; OPENAI is a canonical extra. BZ=F/CL=F/HO=F remain visible as
unsupported dispatcher symbols; dispatcher rules are not weakened.
Two identical frozen runs produced SHA256
`38bd10e475876624891a1057c64d45baf5057db74cffce8133ccdd82034af3b2`.
No successful source scans were supplied, so output explicitly remains incomplete.
An initial run failed on unsupported futures identifiers; this failure led to
explicit adapter-boundary reporting, not silent ticker sanitation.

## Primary historical regression leads

`fixtures/source-excerpts.json` retains tool-extracted primary-source excerpts
and retrieval metadata, NOT full original documents or independently accepted
canonical financial facts. Do not treat excerpt hashes as document hashes.
Marvell IR + SEC accession 0001193125-26-442717 corroborate the MRVL/LITE signed
merger agreement, fixed 4.500 exchange ratio and pending conditions. It is one
economic event affecting two tickers, not completed ownership/cash/revenue.
Athene's October2026 presentation was retrieved, but exact funded exposure
periods were not established by the excerpts; those facts require B03 review.
Neither historical fixture is a fresh material alert. Original documents still
need B03-owned durable capture and complete economic extraction.

## Dependency-ordered continuation

1. B00 #148/#146 + B03 #12: bind issuer identities/source policies for admitted
   instruments (including ADR/foreign mappings) without promoting the scaffold.
2. B03 #12: official incremental source adapter, event identities/revisions and
   authorized legacy canonical persistence; B05 #51 consumes accepted edge proposals.
3. B01: independent source/replay/persistence acceptance at exact heads.
4. B08: verified persistence/Library readback and delivery integration, then run
   acceptance against existing watches before any cutover recommendation.

Both recurring MRIE watches were found enabled; neither was changed. No third
scheduler, automation, database, broad migration or paid agent was introduced.

Local validation:187 orchestration tests,75 integration tests, strict stores,
9 pinned dispatcher tests pass. Pinned B03 validator passes for one SFTBY ledger
and explicitly reports CRWV/AAOI/NVDA absent. These are local results; exact-head
GitHub CI and post-merge acceptance remain separate gates. Intermediate failing
test runs were preserved locally and summarized in replay-evidence.json.
