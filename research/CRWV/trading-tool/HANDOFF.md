# Ownership and integration handoff

Producer **B10 #95**, `work/95-incremental-ticker-patterns`, exclusive writes `research/CRWV/trading-tool/**`. Checked all 24 open PR file lists before implementation; no collision. Other research and shared engines/CI/runtime are unchanged. This is a domain-local operational prototype ready for owner review, not a second canonical traversal engine or a deployed service.

| Receiver | Durable request | Smallest next action |
|---|---|---|
| B00 registry / B06 engine | [#96](https://github.com/whiterosecoffee/_BASKET/issues/96), existing #70/#92 | Register `component.json` in owned `orchestration/planner/worker-library.json`; expose stable `run.py` invocation in ticker discovery. Review adoption into canonical B06 adapter. |
| B08 runtime / B02 data | [#97](https://github.com/whiterosecoffee/_BASKET/issues/97), existing #70/#94 | Supply host credentials and durable volume; supervised one-cycle then service loop, exchange-session lag/entitlement proof and health monitoring. |
| B01 independent QC | [#98](https://github.com/whiterosecoffee/_BASKET/issues/98) | Execute exact producer-head tests and pinned-source replay with zero-test/skip failure; record actual run SHA. |
| B07 calibration | existing [#93](https://github.com/whiterosecoffee/_BASKET/issues/93) | Review features/outcome availability, held-out stability and probability calibration before assigning odds. |

Parent historical source is PR69 commit `6d82bccacaaba9855ef6bd27c64d72eb0514c8c9`. We read/hash its CSVs and pattern records only; no runtime import of its code, no edits, no duplication of the corpus. Detector/score attribution is in `patterns.py`; the local version freezes its implementation hash independently.

Status gates: runnable local component ✓; 26 local tests ✓; pinned historical replay ✓; independent exact-head domain CI pending; shared discovery pending; merged main pending; hosted process **not running**; live trade/NBBO entitlement **not available through MCP**. The polling loop does not transform missing permissions into a live feed. ChatGPT hourly checks are not this runtime.
