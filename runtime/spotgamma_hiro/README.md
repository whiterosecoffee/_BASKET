# SpotGamma HIRO: offline user-export intake

This isolated B02 prototype ingests user-authorized observations, NEVER claims a live feed.
Unknown provider capture time stays null and cannot be traded as live. Licensed SpotGamma
data must not be redistributed publicly without checking terms; fixture below is user-supplied.

Input: JSONL objects with ticker, HIRO USD, 30-day HIRO low/high, optional price,
walls and timezone-aware observed_at. Output: deterministic ID, append-only JSONL.
Run: `python runtime/spotgamma_hiro/hiro.py INPUT.jsonl OUTPUT.jsonl`
Test: `cd runtime/spotgamma_hiro && python -m unittest discover -v`

Do not wire into Massive/TTD until B02 owner and B00 contract review; streaming/export
entitlement, host, TTD, and synchronized price-volume joining remain unresolved.
