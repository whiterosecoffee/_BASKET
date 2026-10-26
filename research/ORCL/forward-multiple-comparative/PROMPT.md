# MASTER PROMPT: FORWARD-MULTIPLE COMPARATIVE ANALYSIS
Status: v0 (unverified, unrun, untested, unmeasured)
Home: _BASKET research/ORCL/forward-multiple-comparative (issue #80). Unmerged v0.
Partition logic: one subject = one chat. This file holds only the reusable engine. Subject-specific state (ticker notes, last scores, saved lookups) lives in the subject's own Project.

## PARAMS (swap per run)
- TARGET = ORCL
- CORE_PEERS (weight in peer median) = IBM 25%, MSFT 25%, SAP 20%, AMZN 15%, GOOGL 15%
- OVERLAY (shown separately, NOT in median) = CRWV (pure AI-infra comp, noisy multiple)
- OPTIONAL SWAP-IN = NOW (use if the question is about the software-seat-shift thesis)
- HORIZON = next reported quarter + NTM
- OUTPUT RULES = USD only; ticker beside every company name; narrow lists, no wide tables; do not define any ticker; bottom line first

## PEER-SELECTION RULE (for any new TARGET)
1. Rank candidates by revenue-segment overlap with TARGET, then GICS neighbors (Quartr list_related_companies).
2. Weight CORE_PEERS by overlap share, max 5 names, no single name over 30%.
3. Any name with negative NTM EPS or an unstable multiple goes to OVERLAY, never the median.
4. State the weights and the reason in one line each.

## STEP 0: FRESHNESS GATE (blocks everything else)
- State first: which markets are open / closed / on holiday today.
- Pull live prices (Massive) and consensus + events (Quartr; web as fallback) every run.
- For each input print: source, data age, TTD (time after which it cannot be used without a fresh lookup).
- If anything cannot be refreshed: say so at the top and label all outputs NON-ACTIONABLE.
- Never reuse stale numbers from earlier in the chat.
- Repo source map: B02 `tickers/<T>/history.jsonl` for prices, B03 `tickers/<T>/events.json` for dated catalysts, B10 `research/CRWV/**` for the CRWV overlay, tracker `orchestration/ticker_trackers/orcl.json` (#75) for ORCL evidence panels. Anything not in an owned store is flagged a gap.

## STEP 1: PASS 1 (cheap, direct answer, 5 lines max)
- Rank TARGET + CORE_PEERS by upside potential from current multiples into next quarter.
- Winner first. Give the one-line reason and one-line invalidation.
- Then ask what depth is wanted for Pass 2. Do not dump.

## STEP 2: PASS 2 (only after Pass 1)

### 2a. Weighted forward multiple (per company)
Default blend:
- NTM P/E 35%
- EV/NTM EBITDA 20%
- EV/NTM Sales divided by NTM revenue growth 15%
- PEG on NTM EPS growth 15%
- EV/NTM FCF 15%
Rules:
- If NTM FCF is negative or capex-distorted (ORCL, CRWV), move the FCF weight to EV/NTM EBITDA and flag it.
- Use consensus NTM, not trailing. Net debt and lease obligations included in EV.
- Show each name's blend vs (a) weighted CORE_PEER median, (b) its own 5-year average.

### 2b. Upside Score (0-100, show the math)
- 40% Re-rating gap: distance from the blend to the lower of peer median or own-history blend, growth-adjusted
- 30% NTM EPS growth, revision-adjusted (30/90-day estimate trend)
- 20% Next-quarter setup: consensus vs whisper, beat/miss history, guidance record, implied move vs historical post-print move, report date
- 10% Risk haircut: net debt/EBITDA, capex-to-revenue, financing dependence (subtract)

### 2c. Reverse-check
- What growth and margin is the current price already assuming for TARGET? Compare to consensus. State the gap.

## STEP 3: BULL CASE THEN INVALIDATION
- Expand first: the clearest, strongest bull case for the top-ranked name, no hedging.
- Then contract: specific, measurable invalidation conditions with thresholds and dates.
- Do not lead with challenges or split hairs over wording.

## STEP 4: WHAT ELSE TO CONSIDER (score each tailwind / neutral / headwind, one line each)
- RPO/backlog size, conversion timing, customer concentration
- Capex plan, debt load, financing and credit-spread risk
- GPU supply, power and data-center delivery constraints
- Cloud growth rate vs Azure / AWS / GCP, and share trend
- Legacy base durability (database, maintenance, mainframe, ERP)
- Margin path and FCF inflection timing
- Estimate-revision momentum
- Options-implied move, gamma positioning (MenthorQ QUIN / SpotGamma, GEX supplied manually if available)
- Institutional holdings changes and insider activity
- Rates and macro sensitivity (1-year backdrop window)
- Regulatory, geopolitical, and customer-vendor-circularity exposure
- 6-month price-pattern window for current behavior; for today / 72h / 10-day range context run `research/ORCL/Range_Traversal/INSTRUCTIONS.md` (issue #81, separate branch until merged)

## STEP 5: DECISION LADDER
- Test and score at least 3 valid framings (T00) before recommending one.
- Ranked scenarios (base / bull / bear) with probabilities and what moves them.
- Decision rules as a ladder: if X then Y, with invalidation triggers.
- Park valid-but-not-next items as ghost nodes, one line each.

## STEP 6: LOG
- Assumptions, gaps, data ages and TTDs, uplift self-score.
- Corrections go first in any response; never bury them.
- Max one open ask per message.
- Final line: "Next step: <queued action>"
