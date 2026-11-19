# CRUS research readiness

B21 #188: [plan](PLAN.md), [owner handoff](HANDOFF.md), [validation](VALIDATION.md).

This small research component identifies why CRUS cannot yet receive a reproducible
current valuation. It preserves a dated source-reviewed snapshot and competing
hypotheses, validates point-in-time and evidence readiness, and returns explicit
blocked states. It does not ingest quotes, verify source truth, compute valuation
or duplicate the B04 optimizer. The contract is local and experimental.

Run the commands in VALIDATION.md from the repository root. `audit.py` uses Python
stdlib only. CLI exits: 0 inputs eligible for owner review; 2 valid but blocked;
1 invalid input. The real checked-in snapshot must return 2.

Use new dated snapshot files for subsequent research revisions. The B00 #192
handoff assigns a canonical CRUS home; B01 #193 independently checks this prototype.
No merge, release, current-price or live-monitoring claim.
