# B19 coverage worker contract and runbook

## Identity and ownership
Spark B19; worker issue #21, branch `work/21-underrepresented-ticker-coverage`, draft PR #23; parent B00. Exclusive paths for this worker: `research/themes/supply-chain/coverage/underrepresented-2026-10-17.json`, `check_coverage.py`, `test_check_coverage.py`, and this new runbook. Read PR #18 registry, B00 contracts and B03/B05 evidence only. Prohibited: `orchestration/**`, `schemas/**`, `tickers/**`, `engines/relationships/**`, `tests/integration/**`, `.github/workflows/**` and all existing PR #18 files.

## Objective and output
Maintain a research-only expansion inventory that identifies potential missing entities and economic segments without claiming canonical registration, market share, revenue or live prices. B00 uses the catalog for identity and prioritization; B19 #17 uses it for research reconciliation; B03/B05 receive verified source and relationship proposals only after review. Candidate JSON has local research schema `basket.b19-underrepresented-coverage@1`; shared contracts stay with B00.

## Discovery and deterministic pipeline
1. **Discover:** Read current main governance, this issue and PR changed filenames. Refuse overlapping writes.
2. **Acquire:** Read the complete B19 PR #18 registry at a pinned SHA and collect dated publisher evidence.
3. **Normalize:** Distinguish listed issuer vs private entity vs ETF, ticker aliases and ADRs. Keep original currency/FX basis for financial facts; never fabricate it.
4. **Verify:** Validate source class and HTTPS link, real publication date and cutoff; mark missing evidence explicitly. A URL is a pointer, not proof its claim has been independently reviewed.
5. **Reconcile:** Compare unique candidate identifiers against baseline IDs; differences are scoped to research registry, not user watchlist.
6. **Calculate:** No current valuations or dollar market shares in this research artifact. If denominator missing, null; do not sum intermediary gross revenue into final spending.
7. **Persist:** Update owned JSON and reference its Git commit plus pinned comparison SHA. Never overwrite historical observations in canonical stores.
8. **Validate:** Run checker and regression tests, with negative cases.
9. **Publish:** Commit to worker branch, draft PR. No merge.
10. **Invalidate:** When registry SHA, company identity, evidence claim/source revision, issuer financial filing or graph contract changes, re-run validation and flag dependent projections for owner review.

Idempotency: candidate ticker + research schema + pinned baseline commit; for evidence use immutable publisher URL + publication date + issuer source ID when known. Repeated identical input must yield the same candidate set. Failed acquisitions remain missing; do not retry infinitely. Source failures are recorded for correction, and partial coverage is not classified as success.

## Commands (from checked-out PR #23)
```bash
python -m unittest discover -s research/themes/supply-chain/coverage -p 'test_check_coverage.py' -v
python research/themes/supply-chain/coverage/check_coverage.py research/themes/supply-chain/coverage/underrepresented-2026-10-17.json
python research/themes/supply-chain/coverage/check_coverage.py research/themes/supply-chain/coverage/underrepresented-2026-10-17.json --registry /path/to/pinned/PR18/tickers.json
```
The optional registry must be the entire original pinned file, not an invented sample. Checker validates structure and explicit declared research-only constraints, **not** web-page truth, corporate identity or financial data.

## Interfaces and failure behavior
Input: B19 expansion JSON and optional PR #18 `mrie-b19-coverage-watchlist@1` registry; stable URL/date/source references. Output: JSON summary of candidate count, sorted IDs, optional baseline count and combined identifiers; exit code 0 only on accepted structure, 1 on evidence/date/duplicate/schema failures. Incomplete corporate identity remains `not_checked`. Source TTD and market-data licensing are B02 responsibilities. Canonical edges are B05; issuer events B03. Recompute upon pinned upstream revision change; no scheduled polling implied.

## QC and acceptance matrix
- Unique research IDs, research-only statuses, valid priorities: checker + negative unit cases; runtime result pending independent execution.
- Evidence HTTPS and real publication dates at/before cutoff: checker + negative unit cases.
- Baseline overlap rejected when supplied: checker + negative unit case.
- Reproducible timestamped issuer financial attribution: **not implemented**; requires B03/B19 #17 source intake.
- Exact-PR-head GitHub CI and domain integration: **not verified**; B01 handoff #52.
- Graph traversal / contracts: **not implemented**; B00 #50 and B05 #51.

## Failure register
1. Original date regex allowed impossible dates. Replaced with calendar parse and cutoff comparison; added tests. Independent test execution pending.
2. Previous environment failed fetching GitHub raw files for Python execution. Connector reads proved exact GitHub files; no test pass should be inferred from these reads.
3. Broad B19 subtree ownership overlaps PR #18 conceptually; worker writes only exact reserved files. New collisions route to B00.
4. Missing MANH and PAYP identity ambiguity require B00 registry reconciliation (#41).

## Lifecycle and reporting
Canonical vocabulary from WORKER_PROTOCOL: `claimed → building → review → component_verified → integrated → closed`, with `integration_blocked` or `withdrawn` when applicable. This PR is **review / integration_blocked**, not component-verified. Record exact SHA, changed paths, test command/outcome, source class, blockers, handoffs and ONE next action in final `basket.worker_resolution@1` issue comment. B00 verifies before promotion.

## Ranked backlog
P0 execute 11 domain tests on exact head and optional pinned PR #18 registry; fix failures. P0 reconcile issuer identities and preserve research-only status. P1 add precise source-review state and capacity/revenue data contracts only after B00 interface decisions. P1 B05 graph read-only MVP, then B01 integration QC. No new planner, worker registry or independent status ontology.
