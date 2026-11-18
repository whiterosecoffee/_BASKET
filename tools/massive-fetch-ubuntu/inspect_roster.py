"""Read archive endpoints and print an advisory report for B02."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path


def read_boundary(ticker, raw):
    row = json.loads(raw)
    if not isinstance(row, dict) or row.get("ticker") != ticker or type(row.get("t")) is not int:
        raise ValueError("invalid archive endpoint")
    return {"t": row["t"], "utc": datetime.fromtimestamp(
        row["t"] / 1000, tz=timezone.utc
    ).isoformat(), "class": row.get("class"), "grain": row.get("grain")}


def inspect(root, ticker, required):
    path = root / ticker / f"{ticker}.jsonl"
    item = {"ticker": ticker, "path": str(path), "coverage": "unknown"}
    try:
        with path.open("rb") as source:
            before = path.stat()
            first = source.readline()
            # Reuse the maintainer inventory's bounded tail read.
            source.seek(max(0, before.st_size - 16384))
            last = source.read().splitlines()[-1]
            after = path.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_ino, after.st_size, after.st_mtime_ns
        ):
            item["status"] = "changed_during_read"
        else:
            item["first"] = read_boundary(ticker, first)
            item["last"] = read_boundary(ticker, last)
            item["status"] = (
                "endpoint_before_requirement" if item["last"]["t"] < required
                else "endpoint_at_or_after_requirement"
            )
    except FileNotFoundError:
        item["status"] = "archive_unavailable"
    except (OSError, IndexError, ValueError, OverflowError):
        item["status"] = "endpoint_unreadable"
    return item


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.home() / "OneDrive/_BASKET/_TICKERS")
    parser.add_argument("--required-through", required=True, help="ISO 8601 timestamp with UTC offset")
    args = parser.parse_args()
    try:
        through = datetime.fromisoformat(args.required_through)
    except ValueError:
        parser.error("--required-through must be an ISO 8601 timestamp with UTC offset")
    if through.tzinfo is None:
        parser.error("--required-through must include a UTC offset")

    receipt = json.loads((args.root / "_FETCH-placement.json").read_bytes())
    roster = sorted(receipt["files"])
    files = [inspect(args.root, ticker, through.timestamp() * 1000) for ticker in roster]
    print(json.dumps({
        "mode": "read_only_advisory",
        "required_through_utc": through.astimezone(timezone.utc).isoformat(),
        "roster_source": str(args.root / "_FETCH-placement.json"),
        "coverage_basis": "First and last records only. Continuity, minute grain, and adjustment are unqualified.",
        "owner": "_FETCH/B02",
        "owner_review": [file["ticker"] for file in files
                         if file["status"] != "endpoint_at_or_after_requirement"],
        "owner_action": "Reconcile stale or unavailable endpoints against retained producer evidence.",
        "files": files,
    }, indent=2))


if __name__ == "__main__":
    main()
