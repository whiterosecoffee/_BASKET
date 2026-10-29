#!/usr/bin/env python3
"""Offline tests for agent routing and one-claim-per-spark detection."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "orchestration" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


routing_v = load("validate_agent_routing")
claims = load("spark_claims")


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.routing = json.loads((ROOT / "orchestration/planner/agent-routing.json").read_text())
        self.registry = json.loads((ROOT / "orchestration/sparks.json").read_text())

    def test_current_routing_valid(self):
        self.assertEqual(routing_v.validate(self.routing, self.registry), [])

    def test_missing_default_rejected(self):
        bad = copy.deepcopy(self.routing)
        del bad["spark_defaults"]["B10"]
        self.assertTrue(any("B10" in e for e in routing_v.validate(bad, self.registry)))

    def test_unknown_tool_rejected(self):
        bad = copy.deepcopy(self.routing)
        bad["spark_defaults"]["B10"] = "nobody"
        self.assertTrue(routing_v.validate(bad, self.registry))

    def test_merge_must_stay_human(self):
        bad = copy.deepcopy(self.routing)
        bad["human_only_actions"] = []
        self.assertTrue(routing_v.validate(bad, self.registry))


class ClaimTests(unittest.TestCase):
    def test_duplicate_open_claims_flagged(self):
        items = [{"number": 1, "title": "[B10] a", "state": "open"},
                 {"number": 2, "title": "[B10] b", "state": "open"},
                 {"number": 3, "title": "[B10] c", "state": "closed"}]
        self.assertEqual(claims.find_conflicts(items), {"B10": [1, 2]})

    def test_label_and_handoff(self):
        items = [{"number": 1, "title": "x", "labels": [{"name": "spark:B06"}]},
                 {"number": 2, "title": "[B06] y"},
                 {"number": 3, "title": "[HANDOFF B10→B06] z"}]
        self.assertEqual(claims.find_conflicts(items), {"B06": [1, 2]})

    def test_no_conflict(self):
        self.assertEqual(claims.find_conflicts([{"number": 1, "title": "[B01] a"}]), {})


if __name__ == "__main__":
    unittest.main()
