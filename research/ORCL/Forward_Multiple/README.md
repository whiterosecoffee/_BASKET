# ORCL Forward Multiple: master prompt and vector index

Status: v0 (unverified, unrun, untested, unmeasured). Issue #80. Reusable: swap TARGET and PEERS to run any ticker.
Partition logic: one analysis vector per file, numbered in run order. This README is the only orchestrator. A vector file never edits another vector's output; it reads the previous vector's output contract.
Sibling vector set: `research/ORCL/Range_Traversal/` (issue #81, separate branch until merged).

## Question this answers
Which of TARGET and its weighted peers has the highest potential for growth from current forward multiples and next-quarter forward earnings, and what else must be considered before acting.

## PARAMS (swap per run)
- TARGET = ORCL
- PEERS = defined and weighted in `01_PEER_SET.md`
- HORIZON = next reported quarter + NTM
- OUTPUT RULES = USD only (convert, state basis and date); ticker beside every company name; narrow lists, no wide tables; do not define any ticker; bottom line first; end with "Next step: <queued action>"

## FRESHNESS GATE (runs before any vector; blocks everything on failure)
1. State which markets are open, closed or on holiday now.
2. Pull prices and consensus live every run. Sources: repo store `tickers/<T>/history.jsonl` (B02), entitled Massive connector, Quartr for estimates, events and transcripts. Web is fallback only.
3. For every input print: source, data age, TTD (time after which it cannot be used without a fresh lookup).
4. If anything cannot be refreshed, say so at the top and label all outputs NON-ACTIONABLE. Never reuse numbers from earlier in the chat.
5. Anything not in an owned store or a timestamped source is a gap. Gaps are shown, not filled.

## RUN ORDER (two passes)
Pass 1, cheap, 5 lines max, then ask what depth is wanted:
- Ranked list of TARGET and PEERS by upside from current multiples into next quarter, winner first, one-line reason, one-line invalidation. Uses outputs of vectors 02 and 03 at summary depth only.

Pass 2, only on request, in this order:
1. `01_PEER_SET.md`: who is compared and with what weights
2. `02_WEIGHTED_MULTIPLE.md`: the blended forward multiple per company
3. `03_UPSIDE_SCORE.md`: 0-100 score with next-quarter setup, tested under three weight sets
4. `04_REVERSE_CHECK.md`: what the current price already assumes
5. `05_FACTOR_CHECKLIST.md`: what else to consider, scored but kept out of the score
6. `06_THESIS_AND_LADDER.md`: bull case first, invalidation, decision ladder, three framings tested

Optional range context: `research/ORCL/Range_Traversal/README.md` for today / 72h / 10-day traversal, used as entry and invalidation reference levels only.

## HANDOFF CONTRACT BETWEEN VECTORS
- 01 emits: peer list, weights, overlay list, rationale line per name.
- 02 emits: per company blended multiple, per-component multiples, discount or premium versus weighted peer median and versus own 5-year history.
- 03 emits: component scores, 0-100 total, rank, rank stability across three weight sets.
- 04 emits: implied growth and margin versus consensus, with the gap.
- 05 emits: tailwind / neutral / headwind per factor with the evidence line and owner.
- 06 consumes all of the above and emits the recommendation ladder.

## ROUTING TO REPO OWNERS (read-only here; no writes outside this folder)
- Prices and history: B02. Dated catalysts and filings: B03. Relationships and partnerships: B05.
- Fundamentals and financing: B04. Traversal: B06. Cross-market and macro composites: B17. CRWV evidence: B10.
- ORCL evidence panels: tracker `orchestration/ticker_trackers/orcl.json` (#75, #77).

## STANDING RULES
- Test and score at least three valid framings before recommending (see vector 06).
- Expand to the strongest bull case first, then contract to invalidation. Do not lead with challenges.
- No forecast probability or price target unless computed from stated inputs with the math shown.
- Corrections go first in any response. At most one open ask per message.
- Log assumptions, gaps, data ages and a self-scored uplift at the end of every run.

## OPEN DECISIONS (B00)
- Keep as prompt documents under this folder, or fold the Upside Score into the tracker as a ninth panel.
- Ownership of `research/ORCL/**`: no ORCL company spark is registered (#76).
