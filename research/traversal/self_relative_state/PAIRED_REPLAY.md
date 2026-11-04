# Paired B06 replay and reproducible mechanism check

Issue #154, draft PR #160. Research specification only.

## First paired test

Freeze #145 episode boundaries, labels, evaluation horizon and #109 range/turnover plus #145 efficiency inputs before evaluation. Explicitly bound #150 geometry to the intended session. Fit and score the same baseline twice on identical eligible events, adding only the five-session percentage change in SMA30 to the second model. This paired comparison supplies the traversal-only control missing from the descriptive M0–M5 ladder. Keep the same training procedure, dates, thresholds policy and alert coverage. Then test other candidates individually. Rank is a transformation of distance, so measure incremental value conditional on distance.

Score compression at observation time. Score continuation, failed stabilization and reversal from subsequent completed bars with frozen breach/reclaim order and horizon. Retain unresolved, censored and order-ambiguous events. Split by date across tickers, keep each battle episode together, purge training outcomes crossing the split and resample contiguous date blocks. Report per-class counts, precision, recall, false reversal confirmations, delay, exclusions and uncertainty at equal alert coverage. Previously inspected November 2–3 examples are exploratory. A null or negative result is sufficient to close the research question.

## Reproduce the synthetic check

Extract the Python block below and run with Python 3 (assertions enabled). No dependencies or historical data. Equal total turnover uses one unit of volume at each synthetic close. The fixture uses signed occupancy over ten sessions as an auxiliary persistence comparison, distinct from the contract’s consecutive-session run length. Percentile is the strict 252-prior-observation variant (452 completed closes for SMA200). Neither choice overrides the contract. Constant prehistory is deliberately artificial. Two reorderings yield identical 20-session range position and SMA30 distance, but SMA30 slope changes from +0.88% to −1.13%. A one-day jump from a flat history gives a top percentile ahead of either possible future. These checks establish information differences only.

```python
"""Run with Python 3. Synthetic mechanism tests only. No market data copied.
Input to features: ordered, contiguous, split-consistent completed session closes
as available at decision time. Caller validates session calendar and provenance.
"""
from statistics import mean
from math import isclose


def features(closes, n):
    if len(closes) < n:
        return dict(distance=None, slope=None, persistence=None, percentile=None)
    averages = [mean(closes[i-n:i]) for i in range(n, len(closes)+1)]
    distances = [price / avg - 1 for price, avg in zip(closes[n-1:], averages)]
    prior = distances[-253:-1]
    return dict(distance=distances[-1],
                slope=averages[-1]/averages[-6]-1 if len(averages)>=6 else None,
                persistence=mean((x>0)-(x<0) for x in distances[-10:])
                if len(distances)>=10 else None,
                percentile=mean((x<distances[-1])+0.5*(x==distances[-1])
                                for x in prior) if len(prior)==252 else None)


def run():
    # Reverse the ordering of the same 20 closes, retaining today's price.
    # Equal volume each day implies equal total traded notional in this fixture.
    path = [90+i for i in range(19)]
    a, b = path+[100], path[::-1]+[100]
    assert (min(a),max(a),sum(a)) == (min(b),max(b),sum(b))
    a, b = [100]*450+a, [100]*450+b
    for n in (10,30,200):
        x,y = features(a,n), features(b,n)
        print(n, x, y)
        assert (isclose(x['distance'],y['distance'])) == (n!=10)
    # A late jump alone creates a displacement with zero prior trending.
    assert features([100]*451+[110],200)['percentile']==1
    assert features([100]*451+[110],200)['persistence']==0.1
    # Both outcomes share exactly the same as-of features.
    for suffix in ([111,112],[99,98]):
        assert features(([100]*451+[110]+suffix)[:-2],200)==features([100]*451+[110],200)
    for n in (10,30,200):
        assert features([100]*(n+251),n)['percentile'] is None
        assert features([100]*(n+252),n)['percentile']==0.5


if __name__=='__main__':
    run()
```

## Resumed evidence audit — 2026-11-04 (research only)

Main refreshed: `25ae331f2774250528fc939e3e7795583f8808a3`.
Inspected PR head: `898c6f892be86526eb42675e12161d169335015e`; draft/open/unmerged.
Relative to handoff `fd7144f10b21f2ef2e225017ae76fb970ab55493`, one documentation commit changed only ORCHESTRATOR_HANDOFF.md. All five files were fetched at the inspected SHA and read. PR main comparison contains exactly these five research paths. This dated audit changes this file only; checks must subsequently be read at the resulting head.

### Canonical reader and coverage gate

Reconciled all five comments on #148. Legacy `tickers/**` remains the physical convention; `runtime.ticker_data.TickerStore(root).read(as_of,...)` is an NVDA-only, explicitly rooted pilot. It is not the B00-approved multi-instrument `resolve(instrument_id,data_kind,access_mode,as_of)` required by #145. Main has no approved resolver/cutover evidence or populated _TICKERS history. The latest recovery request still asks B00 to allocate one private NVDA root and authorize a verified switch. Therefore **BLOCKED_CANONICAL_DATA**; no fallback to legacy or recovery bars for classification.

Inventory below describes inspectable evidence, not eligible replay samples. Requested cutoff: completed sessions through 2026-11-03; latest 200–500 completed daily sessions per symbol plus RTH 1m coverage for every selected episode's discovery, observation and resolution. Exact exchange-session gaps remain unknown until B02 returns a calendar-derived inventory.

| Symbol | Daily evidence on refreshed main | Minute evidence | Replay eligibility / exclusions |
|---|---|---|---|
| QQQ | No history/meta path in complete Git tree | No canonical minute path or snapshot supplied | Eligible n=null; missing coverage inventory, adjustment, availability, revisions and hash; exclude pending resolver |
| NVDA | No daily history/meta path in complete Git tree | #148 reports recovered 2026-10-26–30: 4,690 extended-hours bars, 390 RTH each date; private root unavailable here | Five reported days cannot establish 200–500 daily sessions or all episode ordering; eligible n=null |
| CRWV | Legacy 262 rows, 2025-10-01–2026-10-15; USD, Massive, split_adjusted, completed_daily_bars per metadata | No canonical minute snapshot supplied | 262 unique chronological timestamps, zero invalid OHLC by basic audit; eligible n=null because availability/revisions/calendar and resolver unverified; stale endpoint excludes later sessions |

CRWV exact-byte JSONL: 18,260 bytes; Git blob `66a01994787953af043ccfc0ea58ac5cbeab8736`, SHA-256 `8128c1000b33448c9fb47aa1e28671efc67669faf5d152f8c05b548ea913ef20`. Metadata blob `69329eb9aff49f37a46d37845da276c5dccfbe92` says retrieved 2026-10-16, provider may revise; per-row available/ingested/revision timestamps are absent. No historical-as-of eligibility follows from retrieval. 262 rows would permit at most 63 SMA200 distances and 58 five-session SMA200 slopes if all were eligible; the strict fixture's 252-prior SMA200 percentile needs 452 closes and is unavailable. No assertion that young CRWV has 200 eligible sessions; preserve nulls.

NVDA recovery evidence from #148 (not reproduced here): unadjusted minutes, retrieval-bound availability 2026-11-04T01:56:29Z; raw SHA-256 `05ada8cc2cd464182937cc9f73f9e0a6a71c147fb1fd7625bf065654ab6d9795`, journal `3aecf407ad9f2c2f175ccaaf52240cc01da2707e9b226b4acef5146e0df08470`, snapshot `27c46d04db30f7aa547ab1146aacaa15a54c01e86d9ece8e0d2d01bfbb193038`. Recovery differs from November 1 capture; cannot backdate or mix with adjusted daily data.

Receiving owners: B00 resolver/root/identity arbitration and B02 coverage/provenance, through existing #148. Resume only on an approved read target plus immutable daily/minute manifests specifying calendar, session, adjustment, source IDs, available/ingested times, revisions, hashes, exact gaps and #152 quality policy. Unknown gaps are not “all bars missing.” No bars committed/copied into B06 and no ingestion authorized by this inventory.

### Paired replay readiness and locked comparison

Read #109 metrics at `bdae9fdce9cf647886d52d3319d685deef829095`, #145 controlling README, BATTLE_RANGE_CONTRACT and ACCEPTANCE_CASES at `ea6dcb656fc6c853add9e4906dc4761f64d04813`, and #150 geometry at `eade884d4423e5f7e6a899387e5f62bc3b24045a`. #145 supplies proposed frozen-boundary semantics and synthetic cases, **not a populated frozen historical episode/label manifest**. Episode IDs, numerical discovery/confirmation thresholds and resolution horizons must be frozen by B06/B07 before outcomes are scored; do not invent them from November examples.

Use #109's actual measured range/turnover/efficiency fields without silently substituting #145's absolute-log efficiency definition: #109 uses signed open-to-close progress divided by close-to-close absolute dollar path. Record method/version and any approved adapter. #150, if used, requires explicit calendar-derived RTH `range_start`, completed-bar timestamp conversion and session-filtered inputs; its windows otherwise may include supplied prior-session observations.

Primary arms: existing range/turnover/efficiency baseline versus exactly that baseline plus `SMA30(t)/SMA30(t-5)-1`; t is the latest completed daily session available at observation, never the partial intraday day. Fewer than 35 valid daily closes => slope=null; paired eligibility excludes both arms together with reason. Additional distance/percentile features are not silently added to this first test.

Freeze the event manifest, feature config, model/training procedure, chronological date boundaries shared across tickers, alert budgets and tie policy before label inspection. Keep all connected/overlapping episodes together and purge training episodes whose outcome intervals reach held-out dates. At each predeclared alert coverage use equal alert counts over the identical eligible cohort, training-only tuning and deterministic label-independent tie handling; disclose budgets/thresholds. Compression uses observation-time labels; continuation, failed stabilization and local reversal use their separately frozen completed-bar resolution times. Keep unresolved/censored/order-ambiguous records with distinct denominators. November 2–3 remain exploratory. B17 is a separate third-arm comparison, not part of either primary arm.

Report paired date-block uncertainty for per-class precision/recall differences, counts, false reversal confirmations (count and denominator), onset-to-confirmation delay and censoring/exclusions. If sample support or gain is not durable across held-out dates/tickers, retain the simpler baseline. Current historical result: **NOT RUN**, not a negative result.

| Class | Eligible / resolved n | Baseline precision / recall | +slope precision / recall | False reversal / delay / uncertainty |
|---|---|---|---|---|
| Compression | null | null | null | null |
| Continuation | null | null | null | null |
| Failed stabilization | null | null | null | null |
| Local reversal | null | null | null | null |

All entries are null due to unavailable canonical paired inputs and frozen historical episode manifest, not zero observed events.

### Fresh fixture reproduction and checks

Python 3.12.14, assertions enabled. Extracted the Python fence from the SHA-pinned PAIRED_REPLAY.md using `re.search(r'\x60\x60\x60python\\n(.*?)\x60\x60\x60', text, re.S)`, wrote a temporary script and ran `python3 /workspace/research-snapshot/fixture.py`. Extracted script SHA-256: `cf7cf6bb5f40ec2ecbb5e2a7628dbb56973754c1ec0b9f636b329e6d3ee941e2`. All original assertions passed. Separate arithmetic recomputation verified slope as `sum(closes[-30:])/sum(closes[-35:-5])-1` and 29/34/35-session distance/slope null boundaries.

Both paths: 20-session position 0.5555555555555556, unit-volume notional 1981, SMA30 99.36666666666666, distance 0.006373700100637425. Slopes: +0.00879864636209815 and -0.01127694859038153. This proves mechanism distinction only; fixture does not establish incremental value conditional on all baseline efficiency fields, historical classification lift or future outcomes. Fresh reproduction is independently recomputed arithmetic within this resumed session, not a claimed separate B01 reviewer acceptance.

At inspected head `898c6f8...`, GitHub run [41762550625](https://github.com/whiterosecoffee/_BASKET/actions/runs/41762550625) completed successfully: stores, worker-qc, validate. Workflow explicitly checks out PR head; includes strict store validation, orchestration tests and integration/adversarial QC. It does not execute this Markdown fixture or a historical classifier. Local git clone failed connecting to the environment proxy; source reads and mutations use the connected GitHub tool. No full local repository suite claimed.

**Disposition:** committed design + reproduced mechanism; historical support unknown; canonical replay and independent B01 acceptance blocked. Research only, no merge, no integration or archive-ready claim.
