# B01 component-export qualification

Parent standing guidance: [root AGENTS.md](../../../AGENTS.md). Parent capability:
[B01 exact-source gates](../DOMAIN_SOURCE_GATE.md). Read those first; this node
adds only the connector-export variant. Composition: reuse `revision` and
`strict_result` from [project_sync_gate.py](../project_sync_gate.py), unchanged.

Read [state.json](state.json), then [feature-design.md](feature-design.md) for the
tool contract and [review.md](review.md) for the observed result and next action.
State is a dated record; current GitHub issue/PR/head remains authoritative.

Own only this directory under B01 #272. Source PR264 is read-only B00 #169.
Do not modify its branch, runtime, global catalog, queue or shared workflow.
Select the smallest next action from state. Keep a failed source probe visible;
passing tool regressions do not accept the reviewed source. Before another
component is developed, add its planned instance and owner here or obtain the
appropriate existing-owner scope. Never silently repin a manifest.
