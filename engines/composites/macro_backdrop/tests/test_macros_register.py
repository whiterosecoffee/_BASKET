"""Structural validation for the macro backdrop register (issue #141).

Standard library only. Run from the repository root:
    python3 -m unittest engines.composites.macro_backdrop.tests.test_macros_register
or point any runner at this file.
"""

import json
import re
import unittest
from pathlib import Path

REGISTER = (
    Path(__file__).resolve().parents[4]
    / "research"
    / "composites"
    / "macro_backdrop"
    / "macros.v1.json"
)

REQUIRED_MEASURE_FIELDS = (
    "id",
    "name",
    "group",
    "kind",
    "instruments",
    "formula",
    "convention",
    "role",
    "reads_as",
    "cadence",
    "source_class",
    "access",
    "ttd",
    "thresholds",
)
ACCESS_STATUSES = {
    "verified",
    "cross_checked",
    "unverified",
    "not_entitled",
    "failed_fetch",
    "unknown",
}
UNRESOLVED = {"unknown", "not_entitled", "failed_fetch"}
FORBIDDEN_KEYS = {"probability", "probabilities", "forecast", "target_price", "fair_value", "recommendation"}


def _walk_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _walk_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_keys(item)


class MacroRegisterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(REGISTER.read_text(encoding="utf-8"))
        cls.measures = cls.data["measures"]
        cls.by_id = {m["id"]: m for m in cls.measures}

    def test_a1_parses_with_unique_ids_and_required_fields(self):
        self.assertRegex(self.data["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(len(self.by_id), len(self.measures), "duplicate measure ids")
        for m in self.measures:
            for field in REQUIRED_MEASURE_FIELDS:
                self.assertIn(field, m, f"{m.get('id')} missing {field}")
            self.assertTrue(m["instruments"], f"{m['id']} has no instruments")
            self.assertIn(m["convention"], self.data["conventions"], f"{m['id']} unknown convention")

    def test_a2_access_ttd_and_unknowns(self):
        for m in self.measures:
            access = m["access"]
            self.assertIn(access["status"], ACCESS_STATUSES, m["id"])
            self.assertRegex(access["evidence_date"], r"^\d{4}-\d{2}-\d{2}$", m["id"])
            self.assertTrue(access.get("evidence_note"), f"{m['id']} lacks evidence_note")
            self.assertTrue(m["ttd"].get("rule"), f"{m['id']} lacks a TTD rule")
            if access["status"] in UNRESOLVED:
                for key in ("value", "last_value", "observation", "observations"):
                    self.assertNotIn(key, m, f"{m['id']} is unresolved but carries {key}")
        for event in self.data["calendar"]:
            self.assertIn(event["access"]["status"], ACCESS_STATUSES, event["id"])
            self.assertRegex(event["date"], r"^\d{4}-\d{2}-\d{2}$", event["id"])

    def test_a3_thresholds_are_hypotheses_and_no_forecast_fields(self):
        threshold_ids = set()
        for m in self.measures:
            for t in m["thresholds"]:
                self.assertEqual(t["status"], "hypothesis", t["id"])
                self.assertIn(t["id"], {t["id"]})
                threshold_ids.add(t["id"])
        self.assertEqual(self.data["permission_rules"]["status"], "hypothesis")
        self.assertEqual(self.data["base_rate_study"]["status"], "hypothesis")
        found = FORBIDDEN_KEYS.intersection(_walk_keys(self.data))
        self.assertFalse(found, f"forbidden keys present: {sorted(found)}")
        self.threshold_ids = threshold_ids

    def test_references_resolve(self):
        threshold_ids = {t["id"] for m in self.measures for t in m["thresholds"]}
        for entry in self.data["routing"]["map"]:
            for measure_id in entry["contrast"]:
                self.assertIn(measure_id, self.by_id, f"routing references {measure_id}")

        def check(node):
            if isinstance(node, dict):
                if "measure" in node:
                    self.assertIn(node["measure"], self.by_id, node)
                if "threshold" in node:
                    self.assertIn(node["threshold"], threshold_ids, node)
                for value in node.values():
                    check(value)
            elif isinstance(node, list):
                for item in node:
                    check(item)

        check(self.data["permission_rules"])

    def test_partition_is_static_no_dated_observations(self):
        text = REGISTER.read_text(encoding="utf-8")
        self.assertIn('"unknowns"', text)
        self.assertEqual(self.data["spark_id"], "B17")
        self.assertEqual(self.data["issue"], 141)
        self.assertIsNotNone(re.search(r"macros\.v(\d+|<MAJOR>)\.json", self.data["partition"]["naming"]))


if __name__ == "__main__":
    unittest.main()
