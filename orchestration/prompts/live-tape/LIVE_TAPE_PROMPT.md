# _BASKET live-tape analysis prompt v2.1

Capability: `basket.prompt.live_tape` | version 2.1.1 | mode: prompt | worker issue #205
Supersedes the v1 text in draft PR #187 (pinned `3d148ba`); that file is unchanged.
Repository: https://github.com/whiterosecoffee/_BASKET. GitHub main is authoritative; this prompt is history, not proof.

## Contract (declared inline; adopt the component black-box manifest from #103/#104 when it lands; no competing schema)
- Inputs (defaults): ticker = NVDA; comparators = SMH, QQQ, SPY; session = current regular session; as_of = now, resolved to the latest completed minute actually available; windows = latest 3 completed five-minute windows plus one labeled partial; trade_lookback = 15 minutes; bin_width = $0.25 for NVDA (declare it for any other ticker); data_root = an operator-named durable path or none; hiro = optional supplied snapshot.
- Outputs: report (section 4); write_receipt {added, revised, unchanged, missing, staged_unwritten}; status OK | STALE | UNVERIFIED | BLOCKED | EXPIRED.
- Errors, each naming the missing field or source: BLOCKED_NO_DATA, BLOCKED_NOT_ENTITLED, STALE, UNWRITTEN, CONFLICT_REVISION.
- Classification (#157): CONFIGURE (this prompt) plus REUSE (TickerStore, nvda_pilot resolver, B06 vocabulary). This prompt adds no engine, schema, scheduler, queue or ledger.

## 0. Authority and architecture (read-only, first)
1. For repository work read current main: AGENTS.md, orchestration/PROJECT_INSTRUCTIONS.md, orchestration/WORKER_PROTOCOL.md, orchestration/sparks.json, architecture/VERSIONING.md, runtime/TICKER_DATA.md. Main wins over this prompt; report a conflict first. Unmerged PRs (#109, #125, #145, #150, #153, #157, #187) are context, not authority.
2. Owners: B02 market data, FX, ingestion and TTD. B06 traversal (method code under engines/traversal/**, integrated via #204). B01 independent validation. B00 contracts, schemas and arbitration. B03 events. B07 calibration ledger. Company sparks own only research/<ticker>/**.
3. Ticker-first: methods live once under the owner spark with no ticker names; a ticker holds parameters and results. The NVDA tape_matrix.py in #187 is a research prototype, not the method of record.
4. Analysis chats are not worker chats: no issue or branch unless the owner designates a workstream. Build work: one new issue, one new branch work/<issue>-<slug> from latest main, a draft PR. Never merge, tag or reuse a branch.
5. Never claim a deploy, integration, independent check or receiver action that was not verified. A local replay is not integrated main.

## 1. Data resolution: local first, Massive for gaps
Fix ticker, session and an explicit as-of. Resolve in this order and record which tier supplied each interval:
1. NVDA frozen snapshot: `Pilot(root).resolve('NVDA', 'observations', 'read', as_of)` from orchestration.nvda_pilot.store, then read only through `TickerStore.read(as_of)` or `Pilot.report`. The snapshot is a fixed vintage and coverage ends at its cutoff. Do not open the physical file as an as-of view.
2. Operator-supplied per-date exports (for example the #187 package, one exchange date per file) after verifying manifest hashes.
3. The Massive connector, for the smallest missing or stale interval.

For any ticker other than NVDA no approved writer or resolver exists on main. Use operator-supplied files, else Massive, and treat the results as staged (section 2).

Verify every source: ticker, exchange date, source, schema, adjustment basis, coverage of the requested interval, the prior close needed for returns, and point-in-time availability. A file existing is not coverage. Use the exchange calendar (DST ended 2026-11-01; check auctions, halts, early closes). Separate missing coverage from a verified interval with no eligible trades. Never forward-fill: no-trade minutes are absent. Keep fractional volume as given. Flag VWAP outside [low, high]; do not reject the bar.

Massive rules:
- Probe each endpoint or data class with limit=1 and record the entitlement. The catalog dated 2026-10-17 (orchestration/agentic/massive_workers.json) lists minute and daily aggregates accessible, last trade not entitled, last quote unverified, real-time entitlement unverified, and does not catalog historical trades or quotes. Re-probe after 7 days or on first surprise.
- Treat all Massive data as delayed. State the data age. "As of now" means the latest completed minute actually available. Label operator-typed prints user_supplied.
- Fetch unadjusted minute aggregates for bar metrics. Follow every cursor. Record the half-open interval, timestamp basis, provider, page count and completion.
- Never print raw rows into chat. Aggregate in the workspace SQL or parse tool-saved output files. Workspaces expire after about an hour idle: recreate and re-pull. Same-day row counts can differ between pulls: a later differing pull is a revision, never an overwrite.
- If a data class is not entitled return BLOCKED_NOT_ENTITLED for it. Never substitute VWAP or OHLC for executed volume at price.

Historical replay excludes anything first available or ingested after the cutoff. A later backfill repairs coverage but does not prove decision-time availability. Keep the last trade, the latest completed minute and the latest completed five-minute block distinct.

## 2. Persistence contract
What main can write (verified against runtime/ticker_data.py at b4910122): TickerStore is NVDA-only; the kinds are market_bar and financial_fact only; there is one journal per explicit root at `<root>/tickers/NVDA/observations.jsonl`; put_many commits atomically; an identical repeat returns unchanged; a changed value needs supersedes plus expected_head; the whole file is rewritten and it is not built for trade-tick scale. Importer: `python runtime/ticker_data.py --root <root> import-massive --input <csv> --retrieved-at <UTC> --adjustment-basis unadjusted`. An activated nvda_pilot snapshot is immutable: new data means a new journal root and then freeze, stage and activate by its owner. Never edit an active snapshot.

Tiers:
- W1, NVDA minute bars: write through the importer or put_many to the operator-named durable root, then read back with TickerStore.read(as_of) and compare record IDs and the snapshot hash. B00 ruling R1 (#207, 2026-11-06): one exchange date per file, target layout `<root>/tickers/<T>/intraday/<YYYY-MM-DD>.1m.jsonl` with TickerStore named-field rows. That partitioned writer is not on main yet (owed by B02, #207). Until it ships, give each exchange date its own root so every observations.jsonl holds one date, and refuse to write a batch whose rows span more than one exchange date. Never append a second date to an existing journal; say in the receipt which form was used.
- W2, comparators (SMH, QQQ, SPY), trades, quotes and price-bin evidence: no approved writer or schema exists. Stage recoverable files with sha256, query intervals and page counts, label them UNWRITTEN, deliver them to the operator, and hand off to B02. Never insert trades or quotes into a bar journal.
- W3, never commit provider rows to Git. runtime/TICKER_DATA.md bars this for NVDA. The ORCL-first pilot permission in PR #153 does not extend to NVDA or other tickers without a B00 ruling, and R1 keeps the durable root outside GitHub by default (the pilot is a labeled exception pending a provider-terms check).

With no durable root, write nothing: everything is UNWRITTEN and delivered as files. Chat sandboxes are ephemeral. In a live session persist only completed minutes past the provider delay; the day stays provisional until it settles after close plus delay. Report the write_receipt with counts. If the replay check was not run, say "replay not verified".

## 3. Analysis
Session and participation
- Report session status, last price with time and source, regular-session high and low, the verified prior official close, and regular-session shares to date. Keep premarket, regular and after-hours volume separate. After the close use a verified vendor daily summary for final volume.
- Compare session-to-date and per-window volume with the same clock slot across the prior 20 eligible sessions and report the comparator count. With one prior session name it a single-session comparison. Otherwise leave participation unclassified.

Ease and direction
- Use completed, clock-aligned five-minute windows. Start from the preceding minute close; at the regular open use the first eligible open and flag auction exposure. PR #109 starts a window at the first bar open: state which origin you used (reconciliation is owed to #204). Keep auction windows out of ordinary comparisons.
- Per window report: net USD change and signed USD per minute; shares and signed USD per million shares; shares per absolute dollar for material moves only; path_efficiency = |net| / sum of |consecutive sampled changes| (also called path coherence), stating the unit (the pilot CLI uses USD close-to-close; B06 uses log basis points).
- The near-flat floor is 5 basis points of the starting price, an uncalibrated pilot setting. Label near-flat windows instead of printing inflated shares-per-dollar. Partial windows are provisional and never confirm a shift or an ease flip.
- Directional pair: compare the latest eligible completed window with the nearest opposite-direction eligible window in the same session within the prior six slots, excluding near-flat and auction windows. Report both times, both costs and which direction moved more easily. If no pair exists, say why.
- Read ease with participation. Easy and above typical: momentum candidate, check the close and retest. Easy and below typical: may fail when volume arrives. Heavy with little progress at a tested edge: possible resistance or absorption, separated by rejection, recovery and path efficiency. Weak on quiet volume: little evidence.

Executed volume at price
- Only after the entitlement probe passes, for fully paginated eligible prints: fixed [low, high) bins (NVDA $0.25), summing fractional sizes. State the filter. Report the busiest bin and its shares, the adjacent pocket with exact bounds, and the change versus prior windows. Ties go to the lower price. Flag isolated off-range prints and special conditions. Keep trade sums separate from bar volume. Without entitled trades the analysis is bar-only and labeled so.

Range decision (heuristics, uncalibrated)
- Freeze the active range before testing it. A completed five-minute close beyond an edge is a PROBE. Confirm SHIFT UP or DOWN on a second consecutive completed close outside the same edge, or on a fully paginated modal bin beyond that edge in the same direction. Bars alone need the two-close rule and are labeled bar-only. Report old and new range, confirmation time and evidence; record a revised range as a new observation.
- Keep an ease flip, a confirmed shift and a reversal candidate distinct. A reversal candidate needs a countertrend move, a defended retest, then a break of the prior swing, plus a stated invalidation price.
- Baseline test owed: a prefix-only change-point (CUSUM) run over the same replay. No probabilities until B07 calibration.

Market overlay
- Compare the ticker with its comparators on identical timestamps: matched returns, high-low widths and participation. Default routing: semiconductors to SMH, mega-cap tech and AI software to QQQ, broad market to SPY. Separate flat net returns from true range compression, and move-with-group from divergence, and name which instrument broke or reclaimed its reference first. The comparators are context, not independent proof.

Options overlay
- HIRO comes through the B02 intake route (PR #125) once merged; until then it is operator-supplied, labeled user_supplied and unverified. Timestamp it and compare its change over matched windows with the stock's response. Keep session HIRO, modeled GEX by strike and expiry, published OI and options volume separate. A strike label or net GEX does not establish a pin, gross OI or executed hedging.
- Passive absorption is a hypothesis until eligible trades matched to contemporaneous quotes support aggressor classification; keep ambiguous prints unclassified. Public prints cannot identify a buyer or seller. No causal claims from relative movement and no numeric reversal probabilities.

## 4. Output
Bottom line first, narrow, no ticker background.
1. One line: session | CT as-of | price | active range and state | easier direction | session shares.
2. A narrow table of at most six columns (window, close, bar shares, modal bin, signed USD per million shares, state). Split into two short lists if more fields are needed. Mark unavailable fields.
3. One sentence on market alignment or divergence, plus a separate options sentence when relevant.
4. The strongest bull case first, then the next trigger and its invalidation. Ranked conditional scenarios when asked.
5. Provenance: provider, tier used, latest completed minute, data age, TTD, evidence class per figure, write_receipt, unresolved gaps. For an audit add the replay cutoff, input hashes, method version and tool commit.
6. End with one queued next action.

## 5. Status and evidence rules
Evidence classes: verified observation, company statement, inference, scenario, unknown. For basket.worker_resolution@1 claims map them: verified observation to source_fact; company statement to issuer_statement; vendor or third-party data (HIRO, GEX) to third_party_claim; inference, scenario and unknown unchanged. Every datum carries timestamp, data age, TTD and a status of OK, STALE, UNVERIFIED, BLOCKED or EXPIRED. Historical captures carry ttd_seconds 0 and are never promoted to live. Price levels expire at the session close. Report USD and display America/Chicago; store UTC and the America/New_York exchange date. Probabilities appear only as labeled scenario outputs with formula and parameters.

## 6. Prior-art ledger (status; source class)
- Return per turnover for ease (Amihud, 2002): adopted descriptively, not as impact; repo-cited.
- Path efficiency (Kaufman efficiency ratio): adopted; repo-cited, book not re-verified.
- Same-clock seasonality (Andersen and Bollerslev, 1997): adopted as the 20-session median; repo-cited.
- Temporary versus persistent impact (Hasbrouck, 1991): adopted for retest follow-up horizons; repo-cited.
- Event sourcing and bitemporal records: already implemented by observations.py and TickerStore; cite, do not restate.
- Change-point and CUSUM (Tsaknaki et al., 2024): baseline for the two-close rule, prefix-only; repo-cited. Filtered, not smoothed: the state at t uses data through t.
- Trade classification (Lee and Ready, 1991; Ellis, Michaely and O'Hara, JFQA 35(4):529-551, 2000): deferred until quotes are entitled; the second citation verified by search 2026-11-06.
- Bulk volume classification and VPIN (Easley, Lopez de Prado and O'Hara, RFS 25(5):1457-1493, 2012): deferred; citation verified by search 2026-11-06; published critiques exist on trade-classification sensitivity.
- Order-book imbalance and depth (Cont, Kukanov and Stoikov, 2014): deferred until book data is entitled; repo-cited.
- Market and volume profile, auction-market theory: practitioner literature, not peer-reviewed; the bins and mode here follow it loosely.
- HIRO and GEX: vendor data; hypotheses only.
- Code to review before writing any (titles only; license and quality unchecked): flowrisk, tclf, finmlkit, wraquant microstructure toxicity. In-repo first: PR #109 metrics, PR #150 market geometry core.

## 7. Prohibitions
No raw rows in chat. No invented prices, volumes, bars or coverage. No overwriting evidence. No parallel ledger, queue, scheduler or engine. No claim of a write, review, deployment or receiver action that was not verified. No forecasts beyond labeled scenarios.

## 8. Worked example (illustrative fixture from the #187 draft; not re-verified here)
NVDA, Nov 6 2026, 11:15 CT: $188.08 on 82.26M regular-session shares. In 11:05-11:10, 817K SIP shares traded in $188.25 to under $188.75 with the mode at $188.50 to under $188.75. In 11:10-11:15, 615K shares traded in that range and the mode moved to $188.25 to under $188.50. The 11:15 close fell below $188.25 while the mode stayed inside: a downside probe. At 11:20 a second completed close below $188.25 confirmed a bar-supported downshift. The directional pair was about 2.34M shares per dollar up versus 2.53M down, so upside moved slightly more easily even as later closes confirmed the shift lower. Report both observations.
