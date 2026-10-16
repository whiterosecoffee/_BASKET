# _BASKET — Conversation Sparks and Ownership

**Catalog version:** 1.0.0 · **Coverage:** partial evidence-based synthesis, not a complete export of every ChatGPT transcript.

This project is organized around persistent **objectives** and **exclusive write ownership**, not around chat-history names. Every launched spark becomes one ChatGPT conversation with **its own issue and new GitHub branch**. No spark other than B00 is being started by this catalog commit.

## How to launch
1. Open a **new conversation inside the _BASKET ChatGPT Project**.
2. Say `Launch spark B11` (replace with the ID below), or paste that spark's `launch_prompt` from `orchestration/sparks.json`.
3. The worker reads `AGENTS.md` and the current catalog, inspects issues, creates a fresh issue and branch, then proceeds only within `write_paths`.
4. If GitHub permission is unavailable, do not claim setup succeeded: output a staged issue/branch command and continue read-only analysis.
5. Keep project instructions set to: `For each actionable new _BASKET conversation, read whiterosecoffee/_BASKET/AGENTS.md and orchestration/sparks.json, then perform its mandatory issue-and-unique-branch startup protocol before modifying the repository.`

## Workstream catalog

| Spark | Workstream | Priority | Exclusive write paths | Depends on |
|---|---|---|---|---|
| B00 | Orchestrator & Contracts | P0 | `AGENTS.md`, `orchestration/**` | — |
| B01 | Integrity & CI Rescue | P0 | `tests/**`, `.github/workflows/**` | B00 |
| B02 | Market Feeds, FX & TTD | P0 | `runtime/**`, `fx/**`, `tickers/*/history.jsonl`, `tickers/*/history.meta.json`, `tickers/*/intraday/**`, `tickers/*/live/**` | B00 |
| B03 | Earnings & Event Ledger | P0 | `tickers/*/events.json`, `research/filings/**`, `research/events/**` | B00 |
| B04 | Company Economics & Valuation | P1 | `engines/economics/**`, `engines/valuation/**`, `research/models/**` | B02, B03 |
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

## Prior history mapped into objective-owned sparks

- **Three Holdings Cycle Watch** → B00, B02, B06, B09, B12, B13. GitHub architecture, per-entity history, USD/JPY, SoftBank parent, holdings and 200-session traversal.
- **MRIE Daily Market Capture** → B02, B06, B17, B09, B10, B11. Daily and intraday histories, delta-trim cycles, volume-weighted signals, contextual parent signals.
- **MRIE Earnings Watch** → B03, B04, B07, B08, B15, B18, B19. Earnings and financing, lifecycle economics, bottlenecks, falsification and deployment.
- **SoftBank Parent Watch** → B09, B12, B13, B16, B20. SFTBY/9984.T and ADR, Japanese FX, NAV, OpenAI/ARM look-through, telco/cable edge.
- **AI Infrastructure Portfolio Analysis** → B05, B14, B16, B17, B19. Cross-support among NVDA/CRWV/ARM/NOK/TMUS/SYM/MANH/SFTBY.
- **OpenAI commentary** → B13, B03, B05. Synthetic/private valuation versus actual transactions, neocloud transmission and false assumptions.
- **AI stock market update** → B17, B14, B15, B20. NVDA/ARM/INTC/AAOI/TTMI/AAON/CHTR and macro context.
- **NVDA Stock Valuation Analysis** → B14, B04, B07. Risk-adjusted valuation, hyperscaler expansion and compression of forward expectations.

## Sequencing and collisions
**Launch first:** B01 integrity/CI and B02 TTD/data; concurrently B09 SFTBY, B10 CRWV and B11 AAOI for entity research. B06 traversal uses B02's read-only data; B03 events and B05 graph accept written requests from all ticker/theme workers. B00 resolves contract disputes. B04 valuation, B07 calibration and B08 hosted deployment follow data readiness, without pretending unavailable feeds are live.

**Do not recreate the same broad discussions:** the source conversations intermixed issuer facts, market history, relationship graph and predictive signals. Those are now separate ownership domains. Ticker workers may analyze all inputs but update only their own entity file and research folder.

**Standards:** USD-first; Time to Die expiry; 200+ public-market daily sessions where eligible; evidence provenance; scenario ≠ valuation; unverified inference ≠ signed contract; no fabricated private OHLCV; no double-counted economic flows.

See `orchestration/handoffs.md` for cross-domain changes.

## Explicit coverage limitation
There is no available complete conversation export or API-indexed raw transcript archive in this work session. The mapping uses the accessible _BASKET excerpts, project memory, prior MRIE files and GitHub source tree as of 2026-10-16. Reconcile missing chat transcripts later as new evidence, not as assumed facts.
