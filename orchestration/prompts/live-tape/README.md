# Live-tape operator prompt

[LIVE_TAPE_PROMPT.md](LIVE_TAPE_PROMPT.md) is a paste-ready operator prompt for analyzing live tape for one ticker (NVDA is the worked example). Worker issue #205. Status: draft capability, not integrated main.

## Partition and naming
Operator prompts (agent-invoked, ticker-agnostic capabilities) live under `orchestration/prompts/<capability>/`. Method code stays under the owner spark (`engines/**`, B06 for traversal). A ticker holds parameters and results only.

## Follow the system methodology and architecture
Before any run that touches the repository, read current main: [AGENTS.md](../../../AGENTS.md), [PROJECT_INSTRUCTIONS.md](../../PROJECT_INSTRUCTIONS.md), [WORKER_PROTOCOL.md](../../WORKER_PROTOCOL.md), [sparks.json](../../sparks.json), [VERSIONING.md](../../../architecture/VERSIONING.md) and [runtime/TICKER_DATA.md](../../../runtime/TICKER_DATA.md). Main wins over the prompt.

- Reuse, do not rebuild: read through `orchestration.nvda_pilot` and `TickerStore`; write through `TickerStore` only. No new engine, schema, scheduler, queue or ledger.
- Read local data first. Use the Massive connector only for missing or stale intervals. Persist what the authorized writer can persist; stage and label the rest UNWRITTEN. The prompt states what main can and cannot write today.
- Ownership: B02 data and ingestion, B06 traversal (method code via #204), B01 validation, B00 contracts. Cross-domain changes go through handoff issues, never direct edits.
- Provider data stays out of Git.

## Invocation
Paste the file contents into the agent, then: `Analyze live tape for NVDA, regular session, as of now, with SMH, QQQ and SPY as comparators.` Other tickers, sessions and as-of cutoffs are accepted. Name a durable data root if you want writes; without one nothing is written.

## Status and handoffs
Handoffs filed from #205 (B02 persistence gaps, B14 README relink, B06 additions on #204) are listed in #205. No receiver is assumed to have acted. The v1 text in PR #187 is unchanged.
