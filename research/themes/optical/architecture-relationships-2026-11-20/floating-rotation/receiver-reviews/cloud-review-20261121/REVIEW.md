# Floating Relative Value Rotation Index — scoped source review
Review task B15-312. Source #305 / PR308. Shared implementation #297 / PR298; owner handoff #311.
Verdict: design is usable as a bounded specification; existing engine is not ready for live floating/two-way rotation decisions. Review completed in hosted container; physical Spark pickup and independent receiver acceptance remain pending.

## Checkout and acknowledgment
Requested physical Spark session was not available. Actual host292052b11752, cwd/worktree identity recorded in receiver-ack.json; no native Spark connector found. No source worktree existed in initial task directory. Native public Git read succeeded; a task-local bare clone and detached worktrees were created:
- design f4df492838020f82730382752511fb5342dd12a3
- engine56e9e03693cfcd71cf0ca04d50470332110defda
Both exact HEADs and clean status verified before/after review. No implementation checkout was switched/reset. Sender branch is untouched. Review output gets a separately allocated issue/branch and unique path. Same authoring conversation is not an independent receiver.
Native private _PATTERNS clone failed with could not read Username; connector file access succeeded. Nine files at0758c08 were materialized and each Git blob SHA verified before running its fixture. This is exact file access, not a successful native _PATTERNS clone or Spark authentication.

## Methods resolved
Live _PATTERNS default-branch AGENTS.md, Snapshot.json and Handoff.md read. Index→receipt→state ID/guidance matched:
- _AGENT_FRAMEWORK0758c08f1a8c5451a07df652bfaba985c7f6670b.
- Reviewed skill9b915dcf5f644ca492ae7a3b900c5644025a4d8c and prepared method131830964900dad0d52d6f716643b0cac318d2c1 read.
- _WORKSTATION_HANDOFF59b4a88638293a0c2a5dba12afee269fdd33f934; state identifies historical Spark evidence, not this pickup.
No conflicting published pin found. State/receipt historical expected_head for Agent Framework is older than publication; publication revision was used for read-only execution. Original adoption review is historical; fixture was rerun here.
The Microsoft-derived method separates knowledge access, permission to act and actual receiver acceptance. No Microsoft runtime installation, remote workstation operation or credential transfer performed.

## Commands and actual results
1. git ls-remote https://github.com/whiterosecoffee/_BASKET.git refs/heads/work/305-optical-architecture-relationships -> f4df492... .
2. git clone --bare public _BASKET; git worktree add --detach for the two pinned commits -> exit0.
3. git rev-parse HEAD / git status --porcelain=v1 on both -> exact commits and empty status.
4. python3 -B check_fixture.py in verified _AGENT_FRAMEWORK file snapshot -> PASS synthetic-prepared-checkout-01 (17 checks), exit0. This tests synthetic evidence handling only.
5. python3 -B engines/valuation/rotation/rotation.py engines/valuation/rotation/example.json at56e9e03 -> exit0; captured parent-output.json.
6. python3 -B probes.py <exact-engine-root> results.json -> exit0;10 observation groups including6 one-cent boundary assertions. This confirms observations, including missing guards; it does NOT mean10 operational requirements passed.
No fresh market data requested or used; all probes synthetic. No schedules, trades, merges or shared-engine edits.

## Existing capability versus missing functionality
| Capability | Observed |
|---|---|
| One held ticker to several candidates | Implemented; not all directed pairs or portfolio allocation |
| Scenario EPS×multiple and threshold bid | Implemented; three horizon example |
| Whole shares, per-share sale/buy cost | Implemented |
| Nonfinite quote / future-available forecast | Rejected by probes |
| Nonpositive candidate EPS | P/E unavailable, not ranked as a negative-multiple bargain |
| Required bid at cent boundary | All3 horizons pass at boundary and fail1cent below |
| Residual cash | Intentionally omitted from terminal-wealth hurdle |
| Quotes freshness / as_of / TTD | Not enforced by engine |
| EPS basis / FX / ADR/split provenance | Not enforced |
| Common endpoint consistency | Not enforced across candidate cases |
| Floating fair ratio and two-way state | Design only |
| Tax, dividends, financing, liquidity, margin | External/not implemented |
| Earnings-report rolling forward EPS | Design only |
| Forecast attribution, uncertainty/robustness and replay optimization | Missing |

## Reproduced findings
F1 high-priority input gate: adding as_of2026-11-21 and quote_ttd_seconds1 to old example input has no effect; historical quote input can still emit clears=true. CLI is offline, so this is missing live-use qualification, not evidence it promised a live clock.
F2 high-priority comparable basis gate: held_basis=GAAP and candidate_basis=adjusted are ignored and valuation still returns. The documented supply contract asks callers for consistency; engine does not verify it.
F3 high-priority dated horizon gate: years3/end2035 is accepted beside another candidate's2029 endpoint. This can create unlike rankings if caller validation fails.
F4 documented conservative cash exclusion:1A at100 buys1B at60 plus40cash. At terminal A100/B100, true pre-tax wealth is140 versus100hold; engine requires120sale bid and clears=false because it ignores cash. Preserve the legacy conservative mode, but label it and reconcile residual cash in generalized wealth comparisons.
F5 generalization gap: no direction-specific bid/ask matrix, holdings state/hysteresis or feasible action set. Formula arithmetic is sound, but a review probe is not an implementation.
F6 design precision: gross-price index parity is not total-return/net-liquidation parity when dividends, withholding, financing and taxes differ. Show price-only index separately or derive decisions from the complete net wealth ledger. Per-share corporate EPS purchased is not a dividend and does not determine the justified multiple.

## Material assumptions and failure cases
Very low prior P/Es, flat FX, thin2030 EPS, synchronized fills, quarter interpolation and report-date repricing are NOT validated. Annual checkpoint scenarios cannot identify an optimal trading date. Ratio mean reversion is not established; fundamentals can change permanently. Raw share accumulation need not increase wealth. Switching costs and pathwise margin limits can dominate gross apparent advantage. Illiquid/stale bid/ask and basis mismatches must veto recommendations. Do not retroactively use revised estimates in replay.
Existing review probes confirm estimate revisions can lower thresholds at unchanged prices; they do not supply a point-in-time revision ledger. Horizon roll must be attributed separately. No SNDK/SKHY investment recommendation follows from this code review.

## Smallest useful next B04 increment
Extend the existing #297 input boundary to validate as_of/quote expiry and per-instrument quote timestamps; explicit earnings/instrument basis and common endpoint IDs. Fail closed before clears/ranking. Pair this with terminal residual-cash reconciliation, preserving the legacy conservative option explicitly. Add targeted negative checks for the reproduced cases.
After this boundary is verified, add a pure directed-index view over validated valuations/quotes; then stateful two-way band and portfolio-action evaluation. No duplicate ingestion/model and no live signal until those gates and current inputs are verified.

## Artifact/status boundary
AGENTS.md/state.json, this review, receiver-ack.json, provenance.json, probes.py, results.json and parent-output.json belong only to the allocated review subtree. Original source and engine files unchanged. New branch not merged; independent acceptance and physical Spark checkout remain pending. CI is reported separately against the actual review head.
