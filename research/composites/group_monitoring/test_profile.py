import copy
import json
import unittest
from pathlib import Path
from profile import delta, merge, snapshot


def sample(**kwargs):
    row = dict(id="a", security="NASDAQ:GDYN", metric="revenue", period_end="2025-09-30", duration="quarter", basis="GAAP", currency="USD", unit="currency", provider="issuer", value=100, observed_at="2026-11-19T14:00:00Z", source_url="https://example.org/fixture", supersedes=None)
    return row | kwargs


class ResearchPilot(unittest.TestCase):
    def test_real_baseline_replay_and_duplicate_noop(self):
        rows = [json.loads(x) for x in (Path(__file__).parent/"ai_services"/"observations.jsonl").read_text().splitlines()]
        before = copy.deepcopy(rows)
        saved = json.loads((Path(__file__).parent/"ai_services"/"profile.json").read_text())
        once = snapshot(rows, saved["as_of"])
        twice = snapshot(merge(rows, rows), saved["as_of"])
        self.assertEqual(once, saved)
        self.assertTrue(once["records"])
        self.assertEqual(once, twice)
        self.assertEqual(before, rows)
        self.assertEqual(len({r['security'] for r in rows if r['security']!='FX:USDCAD'}), 4)

    def test_correction_preserves_history_and_knowledge_cutoff(self):
        a = sample()
        b = sample(id="b", value=105, supersedes="a", observed_at="2026-11-20T14:00:00Z")
        rows = merge([a], [b])
        self.assertEqual(len(rows), 2)
        self.assertEqual(snapshot(rows, "2026-11-19T14:30:00Z")["records"], [a])
        self.assertEqual(snapshot(rows, "2026-11-20T14:30:00Z")["records"], [b])
        self.assertEqual(snapshot(rows, "2026-11-18T14:30:00Z")["records"], [])

    def test_reject_collision_and_forked_correction(self):
        with self.assertRaises(ValueError): merge([sample()], [sample(value=99)])
        b = sample(id="b", value=101, supersedes="a", observed_at="2026-11-20T14:00:00Z")
        c = sample(id="c", value=102, supersedes="a", observed_at="2026-11-21T14:00:00Z")
        with self.assertRaises(ValueError): merge([sample(), b], [c])

    def test_comparison_basis_and_period_guards(self):
        a = sample()
        b = sample(id="b", period_end="2026-09-30", value=110)
        self.assertAlmostEqual(delta(a, b, "yoy")["relative_pct"], 10)
        with self.assertRaises(ValueError): delta(a, b)
        for overrides in [dict(currency="CAD"),dict(unit="currency_millions"),dict(basis="adjusted"),dict(duration="annual"),dict(provider="different")]:
            with self.assertRaises(ValueError): delta(a, sample(**overrides))

    def test_missing_and_nonpositive_denominator(self):
        self.assertIsNone(delta(sample(value=0), sample(value=1))["relative_pct"])
        self.assertEqual(delta(sample(value=None), sample())["status"], "unavailable")
        with self.assertRaises(ValueError): merge([], [sample(value=float("nan"))])

    def test_repeat_source_snapshot_requires_no_new_record(self):
        self.assertEqual(len(merge([sample()], [sample()])), 1)
        with self.assertRaises(ValueError): merge([sample()], [sample(id="duplicate-new-id")])


if __name__ == "__main__": unittest.main()
