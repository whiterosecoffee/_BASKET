# _BASKET — Independent Conversation Sparks

> **Start here:** [Conversation Launchpad](LAUNCHPAD.md) — actual launch order, ready-to-paste prompts, worker status and branch-per-conversation bootstrap. The 22-spark registry below is a reference catalog, **not** a request to open 22 chats.

**Complete Project Instructions (single block):** [PROJECT_INSTRUCTIONS.md](PROJECT_INSTRUCTIONS.md)  
**Release policy:** [VERSIONING.md](../architecture/VERSIONING.md) · **Version manifest:** [version-manifest.json](../architecture/version-manifest.json)  
Core baseline: **0.4.1 declared**; target **0.5.0 planned, NOT released**. Catalog version **1.3.0** is independent of the core.

**Catalog:** v1.3.0 · **Objective domains:** 22 · **Coverage:** accessible excerpts and existing artifacts, NOT a full transcript export.

Each spark is a **ready-to-launch workstream**, not an automatically spawned chat. New conversations must read `AGENTS.md` and `orchestration/sparks.json` from **GitHub main**, inspect existing issues/PR file changes, create their **own new GitHub issue and branch** `work/<issue-number>-<objective-slug>`, then modify only exclusively owned files. Dormant sparks have no branches or worker issues.

**Bootstrap:** Until PR #2 merges, new workers READ `AGENTS.md` and the spark catalog from `work/1-conversation-sparks-orchestration`, but CREATE their own issue and branch from current `main`. After approval/merge, read these documents from `main`.

## Launching a spark
Open a new chat inside the _BASKET ChatGPT Project; enter **`Launch spark B01`** or paste the full `launch_prompt` field for B01 from the JSON catalog. The issue+branch initialization should be automatic if GitHub permissions are active. Conversation tools cannot directly launch a second ChatGPT conversation, so user action is needed. New chat != just continuing this thread.

## Launch sequence — gate-driven, not a mass start
- **Wave 0:** B00 — Make workflow bootstrap discoverable from main and resolve baseline schema extension. Gate: Review/merge existing PR #2 after approval, then B00 owns shared contracts..
- **Wave 1:** B01, B02, B03, B21 — CI + facts/TTD + narrative provenance; these can operate in parallel with disjoint writes. Gate: G0 -> G1 and pilot prerequisites.
- **Wave 2:** B06, B05, B09, B10, B11 — Traversal + relationship graph + 3 company research pilots. Research can start while data feed/graph downstream calculations remain blocked. Gate: G1/G2 where outputs require passing tests.
- **Wave 3:** B04, B07, B08, B17 — Valuation, calibration, deployment, and cross-market composites built on verified inputs. Gate: G2 + G3.
- **Wave 4:** B12, B13, B14, B15, B16, B18, B19, B20 — Broaden economic intelligence without losing core operational reliability. Gate: Proof from pilot.

**Immediate pilot launch:** B05 first (handoff #4) to restore strict schema compliance losslessly without a schema change; B01 (handoff #5) independently verifies CI. Then review/merge PR #2 with authorization. **Concurrent active worker recommendation:** 3–5. Research may continue in its own files while output calculations remain blocked by missing upstream data, ownership or CI.

## Authoritative ownership
| Spark | Workstream | Priority | Exclusive write paths | Depends on |
|---|---|---|---|---|
| B00 | Orchestrator & Contracts | P0 | `AGENTS.md`, `orchestration/**`, `architecture/**`, `schemas/**`, `README.md`, `CHANGELOG.md` | — |
| B01 | Integrity & CI Rescue | P0 | `tests/validate_stores.py`, `tests/integration/**`, `.github/workflows/**` | B00 |
| B02 | Market Feeds, FX & TTD | P0 | `runtime/**`, `fx/**`, `tickers/*/history.jsonl`, `tickers/*/history.meta.json`, `tickers/*/intraday/**`, `tickers/*/live/**`, `engines/economics/freshness.py`, `tests/test_ttd.py` | B00 |
| B03 | Earnings & Event Ledger | P0 | `tickers/*/events.json`, `research/filings/**`, `research/events/**` | B00 |
| B04 | Company Economics & Valuation | P1 | `engines/economics/models/**`, `engines/valuation/**`, `research/models/**` | B02, B03 |
| B05 | Ownership & Economic Graph | P1 | `tickers/*/relationships.json`, `engines/relationships/**`, `research/graph/**` | B00, B03 |
| B06 | Traversal & Cycle Engine | P0 | `engines/traversal/**`, `research/traversal/**` | B02 |
| B07 | Calibration, Falsification & Risk | P1 | `engines/calibration/**`, `research/calibration/**` | B06, B04 |
| B08 | Service & Tool Deployment | P1 | `services/**`, `deployment/**` | B02, B01 |
| B09 | SFTBY Parent NAV & Holdings | P0 | `tickers/SFTBY/entity.json`, `research/SFTBY/**` | B02, B05 |
| B10 | CRWV GPU Lifecycle | P0 | `tickers/CRWV/entity.json`, `research/CRWV/**` | B03, B04 |
| B11 | AAOI Optical Manufacturing | P0 | `tickers/AAOI/entity.json`, `research/AAOI/**` | B03 |
| B12 | ARM Royalties & Compute Mix | P1 | `tickers/ARM/entity.json`, `research/ARM/**` | B09 |
| B13 | OpenAI & Anthropic Private Value | P1 | `tickers/OPENAI/entity.json`, `research/OPENAI/**` | B09, B10 |
| B14 | NVIDIA Compute Moat & Capital Loop | P1 | `tickers/NVDA/entity.json`, `research/NVDA/**` | B03, B04 |
| B15 | Optical Bottlenecks: LITE/COHR | P1 | `research/themes/optical/**` | B11, B05 |
| B16 | Telco Edge: CHTR/TMUS/NOK | P1 | `research/themes/edge/**` | B05 |
| B17 | Cross-Market Signal Composite | P1 | `engines/composites/**`, `research/composites/**` | B02, B06 |
| B18 | MU Memory Contract Economics | P2 | `tickers/MU/entity.json`, `research/MU/**` | B03, B04 |
| B19 | AI Supply Chain & Profit Pools | P1 | `research/themes/supply-chain/**` | B05, B04 |
| B20 | CHTR Cable Edge Economics | P2 | `tickers/CHTR/entity.json`, `research/CHTR/**` | B16 |
| B21 | Narrative, Claims & Falsification Engine | P0 | `engines/narrative/**`, `research/narrative/**`, `tests/test_narrative.py` | B00, B03 |

**Test ownership:** engine/ticker unit tests follow their owning domain (e.g. B02: `tests/test_ttd.py`, B21: `tests/test_narrative.py`). B01 owns the shared validator, integration suite and GitHub Actions workflows. B00 owns shared schemas/architecture and contract governance. A test fix cannot justify silencing a genuine contract violation.

## Source conversation refactor
- **Three Holdings Cycle Watch:** B00, B02, B06, B09, B12, B13. GitHub architecture, per-entity history, USD/JPY, SoftBank parent, holdings and 200-session traversal.
- **MRIE Daily Market Capture:** B02, B06, B17, B09, B10, B11. Daily and intraday histories, delta-trim cycles, volume-weighted signals, contextual parent signals.
- **MRIE Earnings Watch:** B03, B04, B07, B08, B15, B18, B19, B21. Earnings and financing, lifecycle economics, bottlenecks, falsification and deployment.
- **SoftBank Parent Watch:** B09, B12, B13, B16, B20. SFTBY/9984.T and ADR, Japanese FX, NAV, OpenAI/ARM look-through, telco/cable edge.
- **AI Infrastructure Portfolio Analysis:** B05, B14, B16, B17, B19. Cross-support among NVDA/CRWV/ARM/NOK/TMUS/SYM/MANH/SFTBY.
- **OpenAI commentary:** B13, B03, B05, B21. Synthetic/private valuation versus actual transactions, neocloud transmission and false assumptions.
- **AI stock market update:** B17, B14, B15, B20. NVDA/ARM/INTC/AAOI/TTMI/AAON/CHTR and macro context.
- **NVDA Stock Valuation Analysis:** B14, B04, B07. Risk-adjusted valuation, hyperscaler expansion and compression of forward expectations.

## Live defects and architectural traps
1. **Failing CI:** at 2026-10-16 GitHub Action 38926002189 fails because `tickers/SFTBY/relationships.json` includes `as_of`, `scope`, `coverage`, `pipeline`, `named_exposures`, and `nav_reference_usd` not permitted by `schemas/relationships.v1.json`. Separate graph data from valuation/context or extend the schema via reviewed migration. B00/B05 source correction; B01 validation.
2. **Narrative engine orphan fixed:** `engines/narrative/**` exists on main but was omitted in v1.0 of the spark catalog. B21 now owns it, with corresponding unit tests.
3. **Two types of stale:** trading quote expiry and quarterly financial statement reporting periods cannot share one unqualified TTL; use period_end, valid_at, observed_at, available_at and ingested_at as appropriate.
4. **Market-data hosting:** GitHub is for code, contracts and curated reproducible snapshots. Persistent high-rate streaming JSONL should live on local/durable hosted storage; Git repository growth is not a feed scheduler.
5. **Ownership conflicts:** matching exact path strings alone cannot detect glob/subtree collisions, nor two simultaneously launched workers with the same spark. Inspect the active issue and PR file list and narrow scopes before writing.
6. **False probabilities:** 200-session descriptive traversal is not a calibrated prediction; no probabilistic trade advantages before B07 point-in-time walk-forward testing.

## First vertical slice
First reproducible three-holdings traversal and intelligence report for SFTBY, CRWV and AAOI, joined to observable compute/FX/financial narrative evidence.

**Required report:** price/bar source and exact as_of or unavailable; daily 5/20/60/200 traversal; intraday short-horizon only if data entitled and fresh; event/relationship evidence and conflict flags; mechanical scenarios with assumptions and falsifiers; risk/costs of trimming vs holding; data age and model version.

**Do not claim:** calibrated next-day probabilities without walk-forward tests; live NAV when holdings/FX/ADR ratios are unresolved; fake continuous feed when adapters disabled; self-directed trading or uncited conviction.

**Release gates:**
- G0: orchestration registry published to main; every task has branch/issue and non-overlapping ownership.
- G1: CI green; canonical entity/event/relationship schemas validate with no relaxed constraints just to pass.
- G2: at least one replayable market feed with explicit TTD and entitlement status; historical and live separated.
- G3: timestamped, source-linked narrative + event ledger, ownership relationship graph and company research can be joined without double counting.
- G4: deterministic report for SFTBY/CRWV/AAOI with range, direction, volume/price velocity and reproducible scenario assumptions.
- G5: walk-forward calibration on held-out windows before any predictive probabilities or risk-adjusted trim edge claims.

## Handoffs
See `orchestration/handoffs.md`. Research domains provide evidence and request event/relationship/schema changes through actionable GitHub dependency issues; they do not modify other owners' canonical files. Cross-domain communication is issue-mediated, not direct ChatGPT-to-ChatGPT messaging.
