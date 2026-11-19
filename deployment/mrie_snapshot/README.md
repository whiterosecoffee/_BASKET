# B08 snapshot component — issue #53, receives #34

Base repository commit: bb2c25fe1052d6ad14699ce213b54334c50383d8.
Source: repository entity@1 records only. Standalone MRIE v10 engines are not copied or deployed.

This is a loopback REST proof component, not a production web server, MCP server, durable ledger, live feed, or native ChatGPT registration. It discovers all ticker entity folders rather than restricting the basket to seven symbols. Missing inputs return unavailable. Existing records are labeled historical_unverified with null as_of; no price or probability calculation exists.

Run from repository root:

```bash
python -m unittest discover -s services/mrie_snapshot -p 'test_*.py' -v
# Set MRIE_ROOT to an immutable checkout, MRIE_SOURCE_SHA to its full commit,
# and MRIE_TOKEN through a secret store (minimum 32 ASCII characters).
python services/mrie_snapshot/app.py
```

Routes: GET /health (public, minimal), GET /tools and GET /snapshot/{ticker} (bearer authentication). Snapshot bytes freeze at startup; every response identifies the configured source SHA and a deterministic snapshot content hash. The configured SHA is an operator assertion, not verified against checkout content: production must derive it from the immutable deployment artifact and verify a build manifest. Code/deployment SHA is not yet reported separately. No current-market validity is claimed.

Six local tests pass: auth/health, frozen provenance, missing/path rejection, global authenticated rate limit, manifest determinism/identity, fail-closed startup config. Tests use synthetic identity-only fixtures, not invented financial observations. Initial fixture assumed ticker key; inspection of pinned canonical entity corrected it to id before publication.

## Orchestrator continuation prompt

Retrieve #53, draft PR for work/53-b08-snapshot-service, and source #34. Refresh current heads, open claims and changed paths. Preserve B08-only services/mrie_snapshot/** and deployment/mrie_snapshot/**. Archive the originating conversation; #53 remains incomplete and #34 remains open.

1. B00 #24/PR #25: register proposed T-015 under existing queue ownership; link #53 as partial REST component. Do not duplicate #33 manager or #48/PR #49 capture dispatch. Fix independent B01 #44/PR #47 QC regressions under existing B00 execution-loop ownership; do not weaken B01 assertions.
2. B01 existing CI owners #44/#45, PRs #47/#46: allocate a NEW noncolliding service integration test/workflow path or formally extend the current owner. Run the six B08 tests plus independent adversarial checks against exact PR head. No generic green validation claim substitutes for this.
3. B08 successor: new issue and unique main-based branch after documented takeover; preserve/reuse this component through reviewed integration. Replace stdlib loopback proof with reviewed production serving and standards-compliant MCP transport. Add build-derived code SHA, validated input manifest, structured redacted logs/metrics, bounded concurrency, timeout/overload handling, and remote auth acceptance tests. Choose authenticated reachable ingress for an external authorized MCP client; a private-network-only host requires an explicit gateway. Verify Render state before provisioning.
4. B02 #11/PR #15 and B03 #12/PR #14: retain ownership of ingestion semantics; B08 supplies storage/hosting adapter only. Agree B00 contracts before implementing append-only durable DB, revisions, deduplication, entitlement/TTD fail-closed behavior and scheduler separation. #43 and #49 are proposals, not integrated contracts.
5. Require real host URL, remote seven-ticker call outcomes (MU/AAOI/NVDA/CRWV/SFTBY/LITE/COHR), code/input SHAs, database restart/redeploy survival, scheduler execution logs, retry/idempotency and repeated-failure alerts. Record measured performance/errors. Only then reassess #34 A1–A6. Missing/expired financial data must stay unavailable.

Current no-overlap inventory: #25 queue/execution loop; #33 agentic manager/audits; #43 architecture; #49 dispatch; #46 OpenAI CI; #47 worker CI; #15 B02 runtime; #14 B03 events; #18/#23 B19 research; #31 B13 research; #38 B21 thesis. Direct access to other ChatGPT conversations is unavailable; GitHub claims and PR paths were inspected, not inferred conversation activity.
