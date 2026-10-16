# SFTBY USD traversal

Daily SFTBY bars are USD-denominated OTC ADR prices. Use `python engines/traversal/sftby_zoom.py --date 2026-10-16` to combine 5/20/60/200-session traversal with the partial-session five-minute zoom.

The intraday capture is a snapshot, not a continuously refreshed stream. Missing five-minute bars may mean no qualifying trades. Range position is descriptive and is not a forecast. USD/JPY historical bars are stored under `fx/JPYUSD/` for subsequent Japanese parent cross-market reconciliation.

**Unresolved:** Massive's U.S. stocks endpoint returned no observations for Japanese ticker `9984.T`. Do not fabricate parent-share prices or infer an ADR conversion factor from missing data. Acquire Japanese-market price history from a suitable provider and verify split and ADR ratios before comparison.

## Holdings integrity
SFTBY's holdings coverage is partial. Official fund category totals are not a full underlying holdings inventory. The historical USD NAV reference is a dated FX translation of previously recorded source figures, not a current estimate. Source-level holdings reconciliation is required.
