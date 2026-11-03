# _BASKET tracked symbol scope

Each folder contains a non-price scope marker. This catalog is separate from existing canonical `tickers/` entity, history, event and relationship data; **no JSONL was migrated**. For a given symbol, later migration needs B02-approved identity/venue/FX mapping, retention of existing immutable data and no duplicate histories. Funds, derivatives, FX and indexes are not company earnings tickers. Inclusion expresses watchlist scope, not a holding or price validation. Folder naming escapes `.` as `DOT_` and `=` as `_EQ_`; USDJPY is a folder-safe alias of USD/JPY.
