# ARM earnings complexity research

Parent guidance: ../../../AGENTS.md; spark B12 in ../../../orchestration/sparks.json.
Read state.json, then feature-design.md. Scope is only this research subtree under Issue #287 and branch work/287-arm-complexity-eps.
Use existing parent truth, currency, ownership and publication rules without duplicating them. Inputs are research snapshots, not canonical records. Run calculate.py to reproduce results.json. Review using review.md. Next action is source refresh and independent PR review; no autonomous merge.

For the forward GAAP variant, read feature-design-gaap-bridge.md and gaap-inputs.json. Run `python gaap-bridge.py --check`; GAAP_BRIDGE.md is its generated readable output. Keep ordinary R&D in adjusted earnings and restore excluded costs once. Preserve filed H1 actuals and label all future recognition schedules as unknown.

For ownership interpretation, read feature-design-assumptions-review.md and generated ASSUMPTIONS_REVIEW.md. Distinguish noncash compensation expense, cash retention, current diluted EPS and future award overhang. Already-GAAP forecast net income must not have SBC deducted again.
