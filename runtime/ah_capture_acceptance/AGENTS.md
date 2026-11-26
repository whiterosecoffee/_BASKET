# AH capture acceptance

Inherit ../../AGENTS.md and ../../architecture/COMPONENT_QUICKSTART.md.
Read state.json, then the selected feature-design.md; state is a record, not a controller.
This node owns metadata only under runtime/ah_capture_acceptance/** for #199.
Reuse the #197 acceptance-node pattern. Existing _FETCH owns source changes and
runtime/refresh_qc; do not create another writer, scheduler, store or validator.
Keep raw provider records and account-private artifact locators out of GitHub.
Verify retained hashes and receiving evidence before changing adoption status.
Review with review.md. Preserve issue/branch; no merge without authorization.
