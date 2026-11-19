# Manual receiver prompt

```text
DOT: take ownership of the operational handoff for the cumulative AI-services group profile (GDYN, EXLS, G, GIB), the first acceptance case for other ticker groups and supply-chain segments.

Read live whiterosecoffee/_BASKET issue #274 and its linked draft PR; then research/composites/group_monitoring/{AGENTS.md,state.json,feature-design.md} and ai_services/{state.json,profile.md}. Inspect existing orchestration/templates and workers before extending or spawning a session. Respect file ownership and private-data rules. The research pilot does not establish an active Spark service.

Establish a formal Spark workstation session with an attributable owner/session ID, durable working directory, checkpoint, dependencies and explicit status. Reuse B02's daily ticker writer and existing premarket/traversal capabilities.

Proposed schedule for applicable US market sessions, America/Phoenix:
04:30 recover interrupted ingestion and retrieve sources;
04:50 validate daily ticker data and freshness;
05:10 compare premarket with prior regular close and after-hours close;
05:20 publish the brief and verified file-update receipts, leaving a retry buffer before 05:30.
Honor market holidays and actual exchange sessions. Tucson is fixed-offset; Eastern time changes seasonally. The schedule remains proposed until scheduler configuration and a completed run are verified.

Use verified USD prices/timestamps, group and QQQ relative performance, 15-minute high/low windows where supported, material earnings/events, and scenarios with triggers/invalidation. Mark missing/stale data. Preserve one trading day per canonical ticker JSONL, duplicate-safe capture and append-only corrections. Return path, trading day, row count, latest source timestamp, content hash and writer receipt for each update.

Keep the separate Monday group-research task and cumulative baseline. Extend comparable operating history, dated EPS revisions, relationship economics and thesis falsifiers. Validate a second segment before claiming generalization.

Return attributable acknowledgment with accepted/deferred/blocked items, owner/session/scheduler identity, first completed-run evidence and the next owner. Do not mark this received or operational merely because this prompt was published.
```
