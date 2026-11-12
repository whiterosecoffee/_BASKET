import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from jsonschema import Draft202012Validator
from orchestration.clean_templates.component import probe

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


class CleanComponentTests(unittest.TestCase):
    def setUp(self):
        self.seed = json.loads((ROOT / "seed.json").read_text(encoding="utf-8-sig"))
        self.request = {"seed": self.seed, "available_capabilities": []}

    def assert_output(self, result):
        schema = json.loads((ROOT / "readiness.schema.json").read_text())
        Draft202012Validator(schema).validate(result)

    def test_manifest_reuses_existing_contract(self):
        schema = json.loads((REPO / "schemas/component-blackbox.v1.json").read_text())
        manifest = json.loads((ROOT / "component.json").read_text())
        Draft202012Validator(schema).validate(manifest)
        for port in manifest["inputs"] + manifest["outputs"]:
            Draft202012Validator.check_schema(json.loads((REPO / port["schema_ref"]).read_text()))

    def test_ready_output(self):
        result = probe(self.request)
        self.assertEqual(result, {"state": "ready_for_local_probe", "errors": [], "missing_capabilities": []})
        self.assert_output(result)

    def test_missing_capability_then_supplied(self):
        self.seed["requires"] = ["capability:worker.review"]
        result = probe(self.request)
        self.assertEqual(result["state"], "blocked")
        self.assertEqual(result["missing_capabilities"], ["capability:worker.review"])
        self.assert_output(result)
        self.request["available_capabilities"] = ["capability:worker.review"]
        self.assertEqual(probe(self.request)["state"], "ready_for_local_probe")

    def test_invalid_seed_is_not_envelope_error(self):
        self.request["seed"] = None
        result = probe(self.request)
        self.assertEqual(result["state"], "invalid")
        self.assertTrue(result["errors"])
        self.assert_output(result)

    def test_malformed_envelopes_rejected(self):
        for request in [None, {}, {**self.request, "dispatch": True},
                        {**self.request, "available_capabilities": "capability:worker.review"},
                        {**self.request, "available_capabilities": ["archive/old.py"]}]:
            with self.subTest(request=request), self.assertRaisesRegex(ValueError, "INVALID_REQUEST"):
                probe(request)

    def test_duplicates_rejected(self):
        self.request["available_capabilities"] = ["capability:read", "capability:read"]
        with self.assertRaises(ValueError):
            probe(self.request)

    def test_repeat_and_no_mutation(self):
        before = copy.deepcopy(self.request)
        self.assertEqual(probe(self.request), probe(self.request))
        self.assertEqual(self.request, before)

    def test_only_owned_schemas_are_read(self):
        self.seed["references"][0]["locator"] = "archive:/absent/implementation.py"
        original = Path.read_text
        def guarded(path, *args, **kwargs):
            self.assertIn(path, [ROOT / "request.schema.json", ROOT / "seed.schema.json"])
            return original(path, *args, **kwargs)
        with patch.object(Path, "read_text", guarded):
            self.assertEqual(probe(self.request)["state"], "ready_for_local_probe")
