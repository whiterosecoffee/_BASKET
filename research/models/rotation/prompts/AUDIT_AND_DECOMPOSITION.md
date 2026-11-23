# AUDIT AND DECOMPOSITION: scoring of AGENTS.md and the prompts, separate purposes, skills, nested-group prior art
Version 1.0.0 | owner B04 | status draft for review | scores are my judgement against the rubric below, not measurements; evidence for each is cited by section.

## 1. Scorecard (0 to 5; 5 = ready to be used by an agent without supervision)
| Dimension | AGENTS.md v1.2.0 | MASTER_MODEL_PROMPT v2.0.0 | RELATIVE_ROTATION_PROFILE_PROMPT v1.1.0 |
|---|---|---|---|
| Single responsibility | 2 (two-point contract plus multiples, tier and zone tracks) | 2 (artifact registry, tiers, relativity, procedures, prior art in one file) | 2 (role, data contract, relationships, fair value, situations, prior art, procedure) |
| Testable and deterministic | 4 (validity gate V1-V8, golden values, tests) | 3 (tier math is testable; tracker reading is prose) | 2 (situations and fair-value exchange are mostly narrative) |
| Evidence discipline | 4 (five evidence classes, provisional rule) | 4 | 3 |
| Universe coverage | 2 (written for the 46-name cohort; golden "9 of 43") | 2 (same; states 9 of 43 while the basket measure is 39 of 243) | 2 |
| Data contract and provenance | 3 (adjustment basis, V4 cross-check; no history file contract) | 3 | 3 |
| Formula completeness for relative movement | 2 (1:x ratios only; no nested-group or sympathy formulas) | 2 | 3 (relationship weights, but not hierarchical) |
| Stop and failure rules | 4 (invalid evaluation must say so) | 3 | 2 |
| Maintainability and versioning | 3 | 3 | 3 |
| **Total / 40** | **24** | **22** | **20** |
Main defects: (1) one file per concern is violated everywhere, (2) coverage statements are cohort-scoped but read as market statements (the cohort was a selection-biased screenshot list; full basket correlation of Friday drop and Monday rebound is -0.79 against -0.41 in the cohort), (3) there is no per-ticker history contract (full OHLCV history existed only as CSV for three names; `history/<T>.jsonl` now exists for NVDA, CRWV, SNDK, MSFT, SMH, QQQ and must be extended), (4) group structure is flat ("theme") with no nesting, (5) "theme" is a hand-assigned peer group, now stored in `cohort/peer_groups_by_industry.json`.

## 2. Separate purposes (explode into independent prompts or agents)
| # | Purpose | Inputs -> outputs | Today lives in | Proposed home |
|---|---|---|---|---|
| P1 | Data steward: ingest, split-normalise, provenance, provisional versus final | vendor bars, filings -> `history/<T>.jsonl`, `fundamentals/*` | scattered | `skills/rotation-data-steward` |
| P2 | Universe and taxonomy: identifiers, groups, nesting | manifest (read only, spark work/146) -> `universe/*` | basket.py only | `skills/rotation-universe-hierarchy` |
| P3 | Two-point comparison | points -> `rotation.compare/1` | AGENTS.md | `skills/rotation-two-point-compare` (AGENTS.md stays the contract) |
| P4 | Valuation: calendarisation, multiples, tiers, EPS-update bands | E, M, bounds -> `rotation.model/1` | MASTER section 3 | `skills/rotation-valuation-tiers` |
| P5 | Relativity: 1:x ratios, ratio statistics, weights to NVDA/MSFT/SMH/QQQ | prices -> profiles | PROFILE prompt | `skills/rotation-relativity-ratios` |
| P6 | Group dynamics and sympathy (nested) | returns, hierarchy -> betas, ICC, residuals | none (new, `sympathy.py`) | `skills/rotation-group-sympathy` |
| P7 | Rotation decision: swap identity, triggers, friction | views -> scenarios | PROFILE sections 5-6 | `skills/rotation-swap-decision` |
| P8 | Evidence curator: news, guidance, consensus with provenance | web, filings -> csv with source and class | PROFILE | `skills/rotation-evidence-curator` |
| P9 | Auditor: validity gates, goldens, change control, scoring | all artifacts -> pass/fail report | AGENTS.md section 4, 9, 10 | `skills/rotation-audit-qa` |
Rule: each agent file states one input set, one output schema, its stop rules, and which other agent's output it may read. P9 reads everything and writes only reports.

## 3. Skills that must cooperate to get the formulas and ratios right
| Skill area | Needed for | Available here |
|---|---|---|
| Market-data engineering | adjustment basis, splits, calendars, provisional bars | Massive MCP; `engines/.../store.py`, `history.py` |
| Fundamental modelling | calendarisation, TTM and forward EPS, reverse DCF, equity duration | `calendarize.py`, `implied.py`; Quartr (needs Pro) and Benzinga estimates are NOT entitled, so consensus is secondary-sourced with a label |
| Cross-sectional statistics | ICC, shrinkage, residual returns, rank statistics | `sympathy.py`, `metrics.py` (stdlib only) |
| Time-series statistics | rolling betas, lead-lag, AR(1) half-life of ratios, volatility-regime correction | `metrics.py` (half-life); rolling beta and lead-lag need history for the whole basket |
| Event-study method | EPS updates, earnings sympathy, abnormal returns | `multiple_events.csv`; needs per-name event dates |
| Portfolio mathematics | swap identity, weights, friction | `rotation.py`, `portfolio.py` |
| QA and testing | validity gates, golden tests | `test_rotation.py`; repo skill `engineering:testing-strategy` |
Other skills in this session (peer comparables, valuation snapshot, earnings reaction, statistical analysis, data validation) can supply cross-checks, but any number they return enters the repository only with a source and an evidence class.

## 4. Formulas for relative movement in nested groups
Notation: log return r_it; hierarchy market M (cohort equal-weight or QQQ) > sector S (SMH for semis) > peer group G > name i; ex-self group return r_G(-i) = mean of r_jt over j in G, j != i.
1. **Level ratio** `x_i/L = P_i / P_L` with P_L an equal-weight or cap-weight group index (ex-self). Track level, z-score and AR(1) half-life as in `metrics.ratio_stats`. A ratio moves because the name moved, the group moved, or both: report `d ln x = r_i - r_L(-i)`.
2. **Sequential (orthogonalised) betas.** `r_i = a + b_M r_M + b_S r_S|M + b_G r_G|S + e_i` where each level is the residual of that level after the levels above (Gram-Schmidt). Report b at each level, R2 added by each level, and e_i (idiosyncratic). Always ex-self.
3. **Sympathy beta and ICC.** `beta_sym = slope(r_i on r_G(-i))`. For one event use the one-way ANOVA intraclass correlation `ICC(1) = (MSB - MSW)/(MSB + (n0-1) MSW)` (implemented). A leave-one-out cohort mean is mechanically anti-correlated with the own value (slope -> -(n-1)), so that regression is invalid and is not reported.
4. **Asymmetry.** Down-beta (days with r_G < 0) versus up-beta. Stress sessions raise correlation mechanically; adjust with the Forbes-Rigobon correction `rho* = rho / sqrt(1 + d (1 - rho^2))`, `d = var_stress/var_calm - 1`, before calling a rise in correlation "contagion".
5. **Small-group shrinkage (empirical Bayes).** `b_i,shrunk = w b_i + (1-w) b_G`, `w = tau^2/(tau^2 + s_i^2)`, with tau^2 the between-name variance of betas in the group and s_i^2 the sampling variance. Needed because most peer groups here have 3 to 10 names.
6. **Lead-lag and information transfer.** Cross-correlation `corr(r_i,t, r_j,t-k)` for k = 0..5 on daily bars, and event-day transfer: abnormal return of peers on a name's earnings day `AR_j = r_j - (a_j + b_j r_M)` summed over the window. Direction (who leads) is a hypothesis until it survives out-of-sample.
7. **Rotation inside a group.** Swap identity within the group is `shares_B = shares_A P_A/P_B`; the group-relative signal is the z-score of `ln(P_A/P_B)` against its own history, accepted only when both names share the group beta within a tolerance (otherwise the swap changes group exposure, not just relative value).
8. **Sympathetic response measure for one event** (implemented, `cli basket`, key `sympathy_peer_groups`): ICC(1) of the move over peer groups, the between-group variance share (biased upward in small groups, so quote ICC), and each name's residual versus its ex-self group mean.
Measured on 2026-11-20 and 2026-11-23 (43 equities in 8 peer groups, Monday provisional): ICC(1) is 0.29 for the Friday move and 0.15 for the Monday rebound; the OLS slope on the ex-self group mean is about 0.5 with R2 0.12 and 0.08. Reading: the Friday flush was shared inside groups to a modest degree, and the Monday rebound was mostly name-specific (NVDA +15 points above its group, INTC and VRT below). One event cannot separate sympathy from common exposure; that needs history.

## 5. Prior art on relative movement in nested groups (cited from memory, verify before relying; evidence grade C until checked)
- Co-movement and category effects: Pindyck and Rotemberg (1990) excess co-movement; Barberis and Shleifer (2003) style investing; Barberis, Shleifer and Wurgler (2005) co-movement from index/category inclusion.
- Industry structure in returns: King (1966) market, industry and firm components; Fama-French industry portfolios; Moskowitz and Grinblatt (1999) industry momentum; Hou (2007) industry information diffusion (big firms lead small); Hong, Torous and Valkanov (2007) industry returns lead the market.
- Linked-firm sympathy: Cohen and Frazzini (2008) customer-supplier momentum; Menzly and Ozbas (2010) supply-chain cross-predictability; Foster (1981), Han and Wild (1990), Freeman and Tse (1992), Thomas and Zhang (2008) intra-industry earnings information transfer.
- Lead-lag: Lo and MacKinlay (1990) cross-autocorrelation of size portfolios.
- Relative-value trading: Gatev, Goetzmann and Rouwenhorst (2006) pairs; Avellaneda and Lee (2010) sector-ETF/PCA residuals with an Ornstein-Uhlenbeck score.
- Hierarchical structure and estimation: Mantegna (1999) hierarchical trees from correlations; Laloux et al. (1999) random-matrix cleaning; Lopez de Prado (2016) hierarchical risk parity; Efron and Morris / James-Stein and empirical-Bayes shrinkage for small groups; multilevel (mixed-effects) models for nested data.
- Stress correlation: Forbes and Rigobon (2002) contagion versus interdependence; Longin and Solnik (2001) extreme-value dependence.
- Selection and testing hygiene: Bailey and Lopez de Prado (2014); Harvey, Liu and Zhu (2016).

## 6. Required changes (tracked, not yet applied unless marked done)
1. Done: `themes.json` renamed to `cohort/peer_groups_by_industry.json`; code reads the new name. JSON schemas still say `theme`; keep the key for compatibility and read it as "peer group".
2. Done: coverage statements in AGENTS.md and MASTER prompt scoped to cohort versus basket.
3. Done: split into nine skills (Agent Skills format, `skills/`). Open: add a history contract (`history/<T>.jsonl`, fields t, date, open, high, low, close, volume; adjusted basis stated in SOURCE.json) and extend it to every priced basket name (about 243 per-ticker fetches; not yet done).
4. Open: hierarchy file (market > sector > peer group > name) for all 297 identifiers; today only 46 names have a peer group and the manifest's `basket_groups` (convexity, general, previous, signals, screenshots) are list buckets, not economic groups.
5. Open: rolling-beta, lead-lag and down/up-beta code (needs history).
