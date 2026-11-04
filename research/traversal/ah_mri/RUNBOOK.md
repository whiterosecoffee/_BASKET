# AH-MRI v0.2 — offline execution and integration boundary

**State:** Experimental B06 report formatter, not live/hosted EOD production. Issue #166, draft PR #168. All changes confined to `research/traversal/ah_mri/**`.

## Run

From repository root:

```bash
python -m unittest discover -s research/traversal/ah_mri -p 'test_*.py' -v
python research/traversal/ah_mri/run.py /path/to/verified-input.json --json-out /tmp/ah-mri.json --md-out /tmp/ah-mri.md
```

Input JSON is the `SAMPLE` shape documented by `test_core.py` (synthetic fixtures are **not market observations**). Every observation MUST supply USD source and time-zone-aware `observed_at`, `available_at`, `ingested_at`, `expires_at`. `session.status=completed` must originate from an external exchange-calendar adapter, never inferred solely from a wall clock. Every report is historical/research only: eligible_as_of means not time-expired, **not proof of current streaming**. `source` must identify the observation provider; a free-text string is not independent provider verification.

The input is a supplied, point-in-time snapshot: nothing is downloaded. `input_manifest_hash` is SHA256 over sorted canonicalized JSON used for this execution, not a canonical market-data revision. No persistent output storage, notification, scheduler, or production-grade service is implemented.

### Report semantics

- RTH close is not overwritten by an AH last trade. OHLCV over RTH and trades/quotes AH must be supplied separately.
- An AH quote is not an AH eligible trade. The RTH close observation timestamp must equal the caller-supplied official session close; AH trades must fall after that boundary and at/before the caller-supplied AH cutoff or default 20:00 America/New_York. The session date must match the regular close's New York date. Expired, future-available, missing or inconsistent AH observations are not shown as an eligible AH mark.
- RTH observations expired at report time may appear as *historical*, with an explicit gap; they are not live current observations.
- `levels.kind=observed` is downgraded to `reference` when calculation, sample window or evidence IDs are absent. Evidence IDs are caller attestations; the prototype cannot independently recompute price-at-volume support. It must not certify a level based solely on those IDs.
- `scenario` intervals remain conditional, uncalibrated. No estimated probabilities or dealer signed gamma are computed.
- Economic surprise = published actual minus point-in-time consensus, only when units agree by caller contract and the consensus was available before release.
- Markdown reports now include the price's provider, observed timestamp and freshness status. `readiness.py` is an explicitly untrusted attestation matrix: even a claimed passing reference never becomes independently verified or releases production by itself. Machine and Markdown outputs must retain `production_ready: false` until external B00/B01 approval and evidence. The core doesn't infer macro causality, session-market-open status, market regime, current dates, economic calendars, trading signals or positions.

### Input trust boundary / preproduction blockers

1. **B02**: authoritative session calendar (including early close), split-adjustment conventions, entitled RTH/extended-hours data, source proofs, `available_at` and TTD, canonical tickers/_TICKERS resolver. This prototype checks timestamps; it does not validate provider entitlements.
2. **B06**: map output from existing #149/PR150 market geometry and #108/PR109 density/range metrics instead of duplicating them. #144/PR145 compression events and #154/PR160 moving-average research are additional optional inputs, *not deployed capabilities*.
3. **B17**: supply synchronized QQQ/SPY, SMH/QQQ, RSP/SPY, IWM/SPY sector/market breadth and universe concentration from #100/PR101.
4. **B00**: determine if/when this proposal merits a published `schemas/**` shared contract. Until then `basket.ah_mri.result@0.2` is *research-local only*.
5. **B01 / B07**: independent exact-commit code tests, full integration CI, point-in-time historical replay, hold/breach score, cost/liquidity sensitivity and quantified calibration. No predictive win rates are supported.

### Acceptance evidence and limitations

- `test_core.py` contains 20 synthetic deterministic tests; `test_readiness.py` contains four additional synthetic readiness checks, not real historical trade/bar replay.
- Do not run a headline report against fabricated data and label it "today"; future market outputs require actual as-of snapshots.
- Do not claim production readiness based on a successful synthetic unit suite or a draft PR.
- No direct merges, releases or cross-spark file writes.

## November 4 source probe — NOT a validated input fixture

Connected Massive historical endpoint `/v1/open-close/{symbol}/2026-11-04` returned SPY/QQQ/NVDA/CRWV/ORCL OHLC, but omitted event-level observed/available/ingested/expiry and official closing-auction eligibility. Volumes contained fractional values; direct close differences against some public summaries require source/adjustment reconciliation. The B02 handoff is recorded in issue #152. **Do not construct invented timestamps to make these bars pass the AH-MRI consumer.** An actual sourced RTH/AH sample, same-clock comparison and provider-vintage manifest remain pending.
