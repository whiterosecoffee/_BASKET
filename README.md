# _BASKET

Versioned economic intelligence, relationship mapping, and market traversal architecture.

See `architecture/` for the specification and `schemas/` for validation contracts.

## Versions and release readiness

Declared architecture baseline: **0.4.1**. Next planned core release: **0.5.0 — Orchestrated Foundation** (not released; strict CI is currently failing). The independent spark catalog version is **1.6.0 candidate** until merged. See [the version policy](architecture/VERSIONING.md), [version manifest](architecture/version-manifest.json), and [complete Project Instructions](orchestration/PROJECT_INSTRUCTIONS.md).

## Operator prompts

Reusable agent prompts live under `orchestration/prompts/`. Start with [live-tape analysis](orchestration/prompts/live-tape/README.md); it requires reading current main (`AGENTS.md`, `orchestration/sparks.json`, `architecture/VERSIONING.md`) before any repository work and reuses the existing writer and resolver.
