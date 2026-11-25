# NVDA tape checkpoint: November 10, 2026

Research owner: B14, [issue #211](https://github.com/whiterosecoffee/_BASKET/issues/211). All prices USD and clock times America/New_York (UTC-05:00). Historical checkpoint through the **completed 12:13 minute**, ending 12:14 ET. This is not a current quote, completed trading-day assessment, prediction or trade recommendation.

## Findings

NVDA's regular-session path remained downward after a high-volume break below $170. The attempted recoveries above $170 did not persist in the subsequent minute closes. The distinction matters: **selling pressure was locally concentrated, but total morning volume was lower than the prior day's matched interval.**

- The 09:30 opening price was $173.97. The regular-session high through this cutoff was $174.69; the low was $166.52 in the 12:03 minute. The 12:13 close was $167.275, about 3.85% below the opening price.
- At 10:44, the one-minute bar moved from $170.36 to $169.71 and contained **5.363394 million reported shares**, 5.916 times the mean one-minute volume in the preceding 10 completed minutes (10:34–10:43). This describes a volume burst during the break, not the quantity sold at exactly $170 or aggressor-classified selling.
- The 11:03 minute reached $170.18 and closed $170.085. The next minute closed $169.68. At 11:15, another attempt reached $170.07 and closed $169.90. These observations support a failed recovery around $170 through this checkpoint, not a claim that every later recovery must fail.
- Regular-session volume from 09:30 through 12:13 was **220.719365 million shares**, versus **245.068667 million** on November 9 over the identical 164-minute window: **90.0643% of the comparison volume, or 9.9357% lower**. This is one prior day, not a statistical relative-volume baseline or a full-day comparison.
- The volume-weighted mean of provider minute VWAPs over the same regular window was approximately **$170.3460**. The $167.275 final minute close was about 1.80% below it. This is an approximate minute-derived measure, not an official daily VWAP.

## Time-window volume context

| ET window, inclusive minute labels | Reported shares, millions | First open → last close |
|---|---:|---:|
| 09:30–09:59 | 68.777815 | $173.97 → $173.17 |
| 10:00–10:29 | 35.280292 | $173.15 → $171.415 |
| 10:30–10:59 | 43.317790 | $171.42 → $168.61 |
| 11:00–11:29 | 32.173942 | $168.615 → $169.0299 |
| 11:30–11:59 | 27.881945 | $169.0308 → $166.8084 |
| 12:00–12:13 | 13.287581 | $166.80 → $167.275 |

The last row has 14 minutes, not 30; its total is not directly comparable to the others. These are shares traded **during intervals**, not a price-volume profile. OHLCV alone cannot reveal absorption, exact-price liquidity, buyers versus sellers, dealer inventory or why the movement happened.

## Source and validation

Massive custom adjusted 1-minute aggregates for November 9–10, sorted ascending with limit 50,000, supplied 1,454 rows. The retained connector table contains all 960 minute timestamps from 04:00–19:59 on November 9 and 494 from 04:00–12:13 on November 10. Both regular-session comparison windows have exactly 164 consecutive minute labels. This clock-grid check does not certify trade-level completeness or final corrections.

The original request/retrieval wall-clock time was not recorded. Concurrent snapshot update timestamps are not substituted for retrieval time. Source currency is USD, adjustment request is `true`, and original historical availability, revision history and independent exchange reconciliation remain unknown. The source is a CSV export of the connector table, not a byte-identical original HTTP response. Its exact retained bytes, query and derived measurements are documented in [evidence.json](evidence.json).

Fractional shares are preserved with Decimal arithmetic. All 1,454 exported volumes are fractional. Twenty-three provider minute VWAPs lie outside their corresponding high/low range, including one in November 10's regular comparison window. These are retained eligibility notices, not automatic corrupt-bar findings, consistent with the prior [B14 source-quality policy](https://github.com/whiterosecoffee/_BASKET/blob/3d148ba1c94c861a45b184e00a697add41fa57ef/research/NVDA/data-recovery/2026-11-04/QUALITY_POLICY.md). No provider values were clipped or repaired.

The private raw export stays outside Git. Only derived research and non-secret provenance are committed. No user-supplied HIRO, holdings, positions or untimestamped quote is incorporated. No current-data freshness claim or canonical import is made.

## Ownership and next step

All 64 open PR file lists were inspected before this allocation; PR187 alone touched research/NVDA, exclusively its November 4 recovery subtree. This checkpoint leaves [#185/PR187](https://github.com/whiterosecoffee/_BASKET/issues/185) untouched and adds no method code. B06 traversal integration remains [#204](https://github.com/whiterosecoffee/_BASKET/issues/204); B02 data persistence and daily-partition acceptance remain [#207](https://github.com/whiterosecoffee/_BASKET/issues/207) and [#183](https://github.com/whiterosecoffee/_BASKET/issues/183). No November 10 canonical JSONL was found in the accessible workspace; other computers were not searched.

Next: B00/B14 review this dated research checkpoint; B02 may separately locate the existing daily store and decide whether the retained adjusted source is compatible before any import. No owner acceptance, merge, live feed, deployment or data-store promotion is implied.
