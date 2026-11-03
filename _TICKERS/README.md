# _BASKET tracked symbol scope

Each folder contains a non-price scope marker. This catalog is separate from existing canonical `tickers/` entity, history, event and relationship data; **no JSONL was migrated**. For a given symbol, later migration needs B02-approved identity/venue/FX mapping, retention of existing immutable data and no duplicate histories. Funds, derivatives, FX and indexes are not company earnings tickers. Inclusion expresses watchlist scope, not a holding or price validation. Folder naming escapes `.` as `DOT_` and `=` as `_EQ_`; USDJPY is a folder-safe alias of USD/JPY.

## Approved additions (2026-11-03)

WDC, NTAP, DLR, JCI, CARR, VICR, MKSI, LIN were added at the user's request. These are tracked scope identifiers, not evidence of holdings or verified price feeds.

## Direction of ownership

The intended future source of truth is `_TICKERS/<instrument_id>/`. Existing `tickers/<symbol>/` paths remain authoritative for data reads and writes UNTIL a coordinated, tested B00/B02/B03/B05/B01 migration changes routing atomically. Never infer a completed migration from this scaffold. See [MIGRATION_HANDOFF.md](MIGRATION_HANDOFF.md). The intended future folder may contain profile, original observations, earnings/filings, evaluations, and other ticker-specific material. Cross-entity event/relationship canonicalization and shared engines retain their domain contracts.
