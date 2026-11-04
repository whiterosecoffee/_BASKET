# AH-MRI acceptance / falsification cases

A1: Timestamp with no timezone or time beyond as_of -> invalid; absent AH trade -> AH mark null; early-close calendar -> no invented 16:00 regular closing price.
A2: One session low only -> reference level, not measured support. No volume-at-price -> cannot claim dollar-volume density. Untyped bands or a precise single-price "panic floor" without support -> fail.
A3: Release actual without timestamped comparable consensus -> surprise unknown; stronger payrolls may be rate-negative and growth-positive, so scenario mechanism must be explicit.
A4: Non-overlapping QQQ/SPY observations -> ratio missing; QQQ RTH and NVDA AH cannot be combined as if synchronized. Futures/ETF settlement differences must be disclosed.
A5: A put strike with OI but unknown dealer inventory -> no signed gamma claim; OI not automatically support.
A6: Observation expires -> historical only; revisions preserve original as-of analysis and change input manifest hash, no silent overwrite.
A7: Frozen replay picks historical as_of -> exclude later economic revisions, late bars and subsequent prices from inputs; score out-of-sample breach/reclaim with fixed horizon.
A8: Breakdown through first reference -> do not automatically call deeper bands observed support; require independent evidence or label scenario.
A9: Quote AH 19:00 ET vs previous RTH close -> both shown and annotated; no AH volume added to RTH volume.
A10: Cross-asset contradictions (QQQ falls while credit/rates ease) -> show opposing evidence and "mixed" regime rather than force causal label.
A11: Return consistent evidence/unknown markers even if no live provider; never claim data feed or monitoring is active.
A12: README, CONTRACT.json and this acceptance inventory all owned exclusively by #166; no schemas/**, runtime/**, engines/**, workflows/** or other active worker paths.

Manual documentation assertions only; executable tests, frozen market replay and independent CI: NOT RUN. Required integration owners: B02 market data/resolver, B06 existing geometry, B17 cross-asset context, B00 shared contract approval, B01 integration verification.
