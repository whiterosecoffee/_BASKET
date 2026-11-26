"""Focused comparison and actual CLI checks, not forecast validation."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch
from compare import compare, context_change, TICKERS, ET

ROOT = Path(__file__).resolve().parents[4]
CONTEXT = ROOT / "engines/composites/market_context/context.py"


def row(day, values):
    return {"t": int(datetime.fromisoformat(day).replace(tzinfo=ET).timestamp()*1000),
            **dict(zip(TICKERS, values))}


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.rows = [row("2026-11-04", [100, 100, 100, 100]),
                     row("2026-11-05", [110, 90, 110, 100]),
                     row("2026-11-06", [121, 99, 99, 100]),
                     row("2026-11-09", [108.9, 108.9, 108.9, 100])]

    def run_comparison(self, rows=None, **kwargs):
        # Independent arithmetic oracle; real-data replay uses pinned B17 helper.
        return compare(self.rows if rows is None else rows, "2026-11-09",
                       "2026-11-10T12:00:00Z", lambda p, b: 100*(p/b-1),
                       windows=(1, 3), correlation_window=3, **kwargs)

    def test_exact_common_window_and_correlation(self):
        result = self.run_comparison()
        self.assertEqual(result["windows"][1]["start"], "2026-11-04")
        self.assertAlmostEqual(result["windows"][1]["price_return_pct"]["NVDA"], 8.9)
        self.assertAlmostEqual(result["windows"][0]["relative_to_qqq_pp"]["NVDA"], -10)
        pair = result["correlation_window"]["pairs"][0]
        self.assertEqual(pair["paired_returns"], 3)
        self.assertAlmostEqual(pair["pearson"], -0.5)

    def test_missing_interior_is_not_forward_filled_or_bridged(self):
        self.rows[1]["NVDA"] = None
        result = self.run_comparison()
        self.assertIsNone(result["windows"][1]["price_return_pct"]["NVDA"])
        self.assertEqual(result["missing_prices"]["NVDA"], 1)
        self.assertEqual(result["correlation_window"]["pairs"][0]["paired_returns"], 1)
        self.assertIsNone(result["correlation_window"]["pairs"][0]["pearson"])

    def test_future_cutoff_and_duplicate_dates_fail(self):
        for rows in (self.rows + [row("2026-11-10", [1]*4)],
                     self.rows + [self.rows[-1]], self.rows[:-1]):
            with self.subTest(rows=len(rows)), self.assertRaises(ValueError):
                self.run_comparison(rows)
        with self.assertRaises(ValueError):
            compare(self.rows, "2026-11-09", "2026-11-09T23:00:00Z", lambda p,b:p/b)

    def test_invalid_price_and_intraday_input_fail(self):
        for value in (0, -1, float("nan"), float("inf"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.run_comparison([{**r, "NVDA": value} for r in self.rows])
        with self.assertRaises(ValueError):
            self.run_comparison([{**r, "t": r["t"]+60000} for r in self.rows])

    def test_constant_series_and_short_history_are_explicit(self):
        result = self.run_comparison()
        self.assertEqual(result["correlation_window"]["pairs"][2]["status"], "constant_series")
        self.assertIsNone(result["correlation_window"]["pairs"][2]["pearson"])
        short = self.run_comparison(self.rows[-2:])
        self.assertIsNone(short["windows"][1]["price_return_pct"]["NVDA"])

    def test_current_dependency_uses_checked_bytes_and_rejects_unknown(self):
        source = CONTEXT.read_bytes()
        with patch.object(Path, "read_bytes", side_effect=[source, b"raise AssertionError('second read')"]) as read:
            self.assertAlmostEqual(context_change(CONTEXT)(110, 100), 10)
            self.assertEqual(read.call_count, 1)
        with tempfile.TemporaryDirectory() as directory:
            unknown = Path(directory) / "context.py"
            unknown.write_text("raise AssertionError('unapproved source executed')\n")
            with self.assertRaisesRegex(ValueError, "pinned PR101"):
                context_change(unknown)

    def test_cli_with_integrated_context_matches_direct_calculation(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "input.csv"
            with data.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["t", *TICKERS])
                writer.writeheader()
                writer.writerows(self.rows)
            actual = subprocess.check_output([
                sys.executable, str(Path(__file__).with_name("compare.py")),
                "--csv", str(data), "--context-module", str(CONTEXT),
                "--cutoff", "2026-11-09", "--evaluated-at", "2026-11-10T12:00:00Z"],
                text=True)
        expected = compare(self.rows, "2026-11-09", "2026-11-10T12:00:00Z",
                           lambda p, b: 100*(p/b-1))
        self.assertEqual(json.loads(actual), expected)


if __name__ == "__main__":
    unittest.main()
