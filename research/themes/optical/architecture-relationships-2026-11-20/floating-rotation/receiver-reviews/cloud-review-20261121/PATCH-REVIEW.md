# Candidate patch: input qualification and residual cash
B15-312 review continuation; B04 implementation request #311. Artifact only; owning engine branch unchanged.
Base engine:56e9e03693cfcd71cf0ca04d50470332110defda, PR298.
Patch changes only engines/valuation/rotation/rotation.py and adds test_qualification_cash.py when applied by owner.

## Result
A candidate delta was applied and tested in a disposable detached worktree. Five unittest methods passed, including11invalid-input subcases. Legacy output fields compare equal against the original engine example. Native git apply --check passed against exact source.
Original source/engine worktrees remained clean. No shared engine ref or main changed. This patch is not an adopted engine release.

## Changes
- Optional qualification metadata: as_of, positive quote TTD, maximum constituent timestamp skew, per-instrument USD identifier/share/earnings basis, common calendar endpoints.
- Qualified mode rejects missing metadata, expired current snapshot, old/future constituent observations, asynchronous quotes, session mismatch, mixed declared earnings bases, non-USD instruments and mismatched calendar endpoints.
- Existing forecast availability/nonfinite checks remain active.
- Legacy fixture remains supported, with metadata_qualified=false and explicit decision_scope=pre_tax_price_only_scenario.
- Adds residual_cash, hold_wealth, switch_wealth, wealth_edge and clears_including_cash.
- Preserves legacy required_bid/clears as a conservative cash-excluded threshold, explicitly labeled legacy_threshold_cash_mode=excluded. New cash-inclusive threshold solving is deferred; do not mix those outputs.
- Example with sale cost1/buy cost1:100sale yields99proceeds, buys1share at60+1cost, retains38cash. Terminal B100+cash38=138 vs100hold. Cash is counted once.

## Reproduction by B04
1. Retain a clean reference checkout of base56e9e03 for original rotation.py/example.json.
2. In separate owner-cleared candidate checkout at that base, run git apply --check PATH/qualification-cash.patch, then git apply PATH/qualification-cash.patch.
3. Set ROTATION_REFERENCE_ROOT to the clean reference engines/valuation/rotation directory and PYTHONPATH to candidate engines/valuation/rotation.
4. Run python3 -B -m unittest discover -s engines/valuation/rotation -p test_qualification_cash.py -v.
5. Run candidate rotation.py against candidate-example.json (synthetic input).
Expected5tests pass. Tests import the original module to compare legacy fields, so the reference directory must remain unpatched.

## Boundaries and next step
Validation checks supplied metadata consistency, not the truth of provider/issuer records, instrument conversions, forecast quality or recurring EPS adjustments. Calendar endpoints use a declared year-offset convention, not an exact year-duration/rolling NTM convention. Cross-scenario pairing, instrument market calendars/halts, dividends, tax, financing, broker feasibility and cost-aware reverse bands remain unsupported.
metadata_qualified=true must never be interpreted as live-trade eligibility. Synthetic fixtures remain synthetic even with internally consistent timestamps.
No taxes/dividends/financing or input data acquisition are added; cash earns zero. No new ingestion/forecast engine or optimizer.
Next B04 action: review/apply candidate into the owned branch, independently verify cases, then add cash-inclusive threshold search before directed-index/stateful action output.
