#!/usr/bin/env python3
"""Strict relationships@1 contract regression tests; no production data mutation."""
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "schemas/relationships.v1.json").read_text())
EXTRA_FIELDS = ("as_of", "scope", "coverage", "named_exposures", "pipeline", "nav_reference_usd")


def minimal_relationship():
    return {
        "schema": "relationships@1",
        "entity_id": "SFTBY",
        "pools": [],
        "upstream": [],
        "downstream": [],
        "ownership": [{
            "target": "OPENAI",
            "type": "equity",
            "sources": ["https://example.org/source"],
            "confidence": "verified",
        }],
        "other": [],
    }


class RelationshipContractRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Draft202012Validator.check_schema(SCHEMA)
        cls.validator = Draft202012Validator(SCHEMA)

    def test_canonical_record_is_valid(self):
        self.assertEqual(list(self.validator.iter_errors(minimal_relationship())), [])

    def test_unknown_context_fields_remain_rejected(self):
        self.assertIs(SCHEMA.get("additionalProperties"), False)
        for field in EXTRA_FIELDS:
            with self.subTest(field=field):
                record = minimal_relationship()
                record[field] = None
                self.assertTrue(list(self.validator.iter_errors(record)), field)

    def test_unknown_edge_field_remains_rejected_if_contract_disallows_it(self):
        # The current edge contract has no additionalProperties:false.
        # Avoid claiming strictness beyond the actual v1 schema.
        self.assertNotIn("additionalProperties", SCHEMA["$defs"]["edge"])


if __name__ == "__main__":
    unittest.main()
