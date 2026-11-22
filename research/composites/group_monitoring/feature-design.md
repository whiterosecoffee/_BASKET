# Cumulative group research, version 0.1.0

Recurring briefs need durable evidence to distinguish period growth, same-period
forecast revision, repricing and new disclosures. This parent supplies a numeric
ledger and deterministic projection; segment definitions belong in children.

## Contract

Input: JSONL facts keyed by security, metric, period_end, duration, accounting
basis, original currency, unit and provider. Immutable IDs carry value (or null with
missing_reason), unit, source URL/class/publication date, effective period,
observed_at, ingested_at, available_at (null if unknown), validity and method version.
Zero is a value. A metric's unit and meaning must remain stable.

Output: profile.json, a deterministic as_of projection, method version and SHA-256
of selected canonical JSON records. profile.md interprets evidence. state.json
records ownership/status/pointers; none of these files executes a controller.

merge rejects conflicting immutable IDs and requires supersedes for corrections.
A correction must reference the latest matching fact and have later observed_at.
Exact repeats are no-ops. snapshot uses this ledger's observation time, so a 2025
fact first retrieved in 2026 cannot appear in a 2025 replay. This is not a historical
trading backtest or a reconstruction of public source availability.

delta requires matching security/metric/duration/basis/currency/unit/provider plus
same reporting period for revisions or matched year-over-year dates. Relative
change = (new / old - 1) * 100 only when old > 0; otherwise null. Absolute change
in percent metrics means percentage points. Missing operands yield null.
Human review still governs peer comparability; EBITDA and EBIT are not equivalent.

Run the read-only CLI with ledger path and --as-of; it writes stdout only.
Stage the ledger and projection together, validate, commit, then read back the
remote revision before advancing a successful publication checkpoint.

## Reuse and limitations

Pinned references in state.json reuse B17 #118/PR120 cohort reasoning and B19
#17/PR18 relationship semantics. #119 and #130 retain canonical contract ownership.
Component index PR225 and Copier PR135 were inspected. No shared schema,
central index or project generator is added.

Six focused tests cover real-baseline replay, duplicate reruns, correction history,
collision/fork rejection, missing/nonpositive values and comparison guards.
Interrupted-publication recovery, real successive runs and second-segment acceptance
remain unverified. Issuer statements are evidence of disclosure, not independently
proven business outcomes. No predictive probabilities or automatic valuation ranks.

Validation command:
python -m unittest discover -s research/composites/group_monitoring -p 'test_*.py' -v
