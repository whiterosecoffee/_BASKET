# CREDIT Stage 0 — dated evidence inventory

Authoritative intake: [#136](https://github.com/whiterosecoffee/_BASKET/issues/136), architecture [6621033985](https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6621033985), resource handoff [6621094932](https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6621094932). Execution worker: B00 #162, `work/162-credit-stage0`, new files under `orchestration/credit/**` only. No merges, tags or releases authorized.

Primary objective: observed market premium minus independently justified premium, with uncertainty. Full-basket coverage, staged delivery. This directory contains a **dated audit projection and contract decision**, not another ticker registry, market-data store, credit ledger or execution queue. GitHub Issues remain authoritative. Source facts remain in their domain-owned canonical stores. No raw licensed prices are copied here.

## Coverage and limits

`coverage-2026-11-04.json` contains one reference row for each of the 291 identifiers in the pinned, unmerged #147 manifest: 198 provisional equities/ADRs, 59 funds/ETPs, 30 indices, 3 futures, 1 FX pair. That manifest is a scope list, not a verified issuer/security master. All issuer IDs remain null until #148 resolves identity. Multiple listings may refer to one issuer; 291 identifiers must never be reported as 291 borrowers.

Each row explicitly covers transactions, quotes, CDS, loan terms, SOFR/Treasury curves, filings, maturities, covenants, collateral, guarantees and fund flows. `unavailable` means no qualifying evidence verified by this repository audit; it does **not** assert that the real-world issuer has no debt or that no public source exists. `not_applicable_direct_issuer_conditional_on_scope_type` is conditional on the provisional index/futures/FX classification. Fund borrowing and look-through exposure need review rather than a no-debt assumption. Shared resource timestamp/entitlement defaults are explicit and apply to every cell. Unknown publication times are not replaced by audit time.

Current verified matched credit prices: **0**. Independently verified issuer identity mappings in this audit: **0**. Historical CRWV terms are referenced from draft PR #69 and require primary-source re-verification. This does not establish current balances, loan availability or market premiums. No issuer receives a zero credit-risk score for missing data. The matrix covers every scope identifier; external issuer-by-issuer completeness and full applicability verification remain pending.

Reproduce using the **exact bytes** of `_TICKERS/manifest.json` at `321c93c281aeeb7d63b5d107cca6a320070d5f02` (Git blob `876c729bedeaebfeb867a51cde591118cf32aa75`), fetched through GitHub. Do not copy that registry into this directory.

```sh
python orchestration/credit/coverage.py --manifest /tmp/basket-manifest.json --output /tmp/coverage.json
python -m unittest discover -s orchestration/credit -p 'test_*.py' -v
```

The CLI rejects mismatched source bytes; changed universe membership needs an explicit new source pin and dated audit. Seven synthetic negative/missingness tests are local component evidence, not financial validation or B01 independent acceptance. Initial source-byte validation rejected a retrieval-added newline; exact source bytes were restored and the generation rerun successfully. No validator was relaxed.

## Reconciliation

Main inspected: `25ae331f2774250528fc939e3e7795583f8808a3`. Read main AGENTS.md, sparks catalog 1.6.0, WORKER_PROTOCOL.md, compiled worker scopes and PROJECT_MAP.md. The compiled queue is historical planning, not current ownership. The initial 45-PR count was an off-by-one reporting error: 46 candidate changed-file lists were rechecked, then 8 newly published PRs discovered before publication, for 54 open PRs and no collision in this subtree. `repository-audit.json` retains those path lists and candidate head/CI evidence. Open PRs are not a worker activity count; capacity remains unknown. No other conversation's branch was reused.

Newly discovered draft PR #173 is an NVDA-only frozen-source resolver pilot on `work/148-nvda-resolver-pilot` at `bbc4ccc45374b79f5f9583f4a060c8b36f3ae43c`. Reuse that candidate under #148; do not duplicate it or assume a CRWV/ORCL/full-basket resolver exists. PR #172 is a separate general resource reconciliation audit; its files do not overlap this credit-specific projection.

Important correction to originating audit: main already contains `runtime/observations.py` recovered from PR #15 by merged PR #140, alongside NVDA-only `runtime/ticker_data.py` and `schemas/ticker-data.v1.json`. This is not a general debt-observation adapter or full-basket resolver. PR #15 itself remains unmerged and its exact-head shared CI failed. Do not generalize the NVDA-only adapter to CRWV/ORCL or credit kinds without its owner.

PR #90 also has real independent financial CI at workflow head `f07763d929b383b5bef8927007a2d51ef1fe5460`, run [40919835438](https://github.com/whiterosecoffee/_BASKET/actions/runs/40919835438), job `123609743311`. Retrieved workflow and job logs verify pinned B10 source `7a33a6f49a2740a93310fa1c66a8090c25dd110a`, **39 tests** and four-scenario demo. This pinned checkout is separate from workflow head. B00 additionally retrieved all 24 PR #87 files, ran 39 tests locally and executed its demo: unfunded case first gap month 1 with null value; three funded cases have no gap under their explicit synthetic assumptions. These are synthetic fixtures, never CRWV forecasts or current valuations. Preserve the B10 implementation; do not rebuild its waterfall.

## Stage disposition

| Stage | Completed in this increment | Pending gate |
|---|---|---|
| 0 | Scope-complete provisional evidence/missingness projection; reusable candidates and source-access routes | Verified issuer applicability, entitled source manifest, independent inventory CI |
| 1 | CRWV historical candidate reference; CRWV/ORCL/NVDA pilot requirements | Primary instrument IDs/terms and comparable current observations; approved resolver/ports |
| 2 | Matched-peer baseline and calibration acceptance specified | B04 implementation, peer dataset, B07 held-out evidence; all spreads/intervals null |
| 3 | Existing B10 tests/demo and B01 pinned-source run verified | Generalization, real input vintages, covenant/conditional-capacity/FX gaps; B05/B21 connections |
| 4 | Existing B06/B08 consumer boundaries retained | Compatible tested components; no alerts or runtime launched |
| 5 | Local inventory tests and existing financial-component evidence | Independent B01 credit integration, exact-head CI and later authorized main verification |

Next action: B02 responds on existing #70 with the CRWV/ORCL/NVDA instrument-price/benchmark coverage and rights manifest, preserving unavailable states. In parallel, B00 #148 resolves canonical identity and #103 ratifies shared ports. See `INTEROPERABILITY.md` and `RESOURCES.md` for concrete receiver contracts. Archiving the originating conversation is safe; #136 and implementation work remain open.
