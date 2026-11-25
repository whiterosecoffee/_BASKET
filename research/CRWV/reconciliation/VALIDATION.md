# Executed validation and attempts

1. Source recovery: current main433d357 and all91 open PR changed-file lists
   inspected. No reconciliation subtree overlap. Existing company tool, CI and
   traversal ownership retained. Worker capacity remains unknown.
2. Initial audit:9 tests passed. Manual review identified that future forward
   estimate values were labelled unqualified but still rendered diagnostically.
   Corrected by redacting future EPS/ratio/residual. Added a focused regression.
3. Corrective execution:10 tests passed, zero skips/failures. Real CLI execution
   produced JSON/text; deterministic replay, missing/nonfinite numeric values,
   strict timestamps, source date cuts, GAAP/adjusted arithmetic, debt/principal,
   cash conservation, conflicting basis and expected-versus-received funding tested.
4. Test fixtures: reported historical arithmetic is source-derived; positive
   forecast gate example is explicitly synthetic and is not a CRWV forecast.
5. Captured original B01 job logs show39 tests and four scenario demos on pinned
   source7a33a6f via workflowf07763d. This is historical independent execution,
   freshly retrieved now, not a newly launched run or integration evidence.

Current PR/source SHA and CI conclusion are posted in #91 resolution after
publication. New reconciliation tests are not registered in shared CI; B01 owner
acceptance is pending. A shared green workflow must not be counted as their run.
No source, workflow, shared schemas, canonical feeds or other research were edited.
