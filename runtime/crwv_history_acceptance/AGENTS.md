# CRWV historical acceptance node

Inherit the repository standing guidance from ../../AGENTS.md and method from
../../architecture/COMPONENT_QUICKSTART.md on the main revision recorded in
state.json. Follow current user instructions where older policy conflicts.

Read state.json first, then feature-design.md only for the selected capability.
This B02 node owns runtime/crwv_history_acceptance/** under existing #196/PR197.
PR122 owns source research and proposed data; B00 owns routing; B01 owns shared
acceptance CI. No new raw observations in GitHub, canonical writes or merges.

Use state.json as this node's dated record, not a controller or replacement for
live GitHub evidence. Refresh source/main/PR heads before working. Reuse current
issue and branch. Run the smallest useful exact-source audit or consumer probe;
retain old evidence and update current evidence pointers. Re-read new source
changes before supplying --expected-source; an explicit SHA is not approval.

Review: verify unchanged source, lossless hashes, failure behavior, real consumer
compatibility and remaining authority gates. Distinguish local proof from B01
acceptance, integration and operation. See review.md for the latest result.
