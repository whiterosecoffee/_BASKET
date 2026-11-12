import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("clean_seed_validator", ROOT / "validate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class CleanSeedTests(unittest.TestCase):
    def setUp(self):
        self.seed = json.loads((ROOT / "seed.json").read_text(encoding="utf-8-sig"))

    def test_seed_is_ready_not_accepted(self):
        self.assertEqual(module.validate_seed(self.seed, [])["state"], "ready_for_local_probe")

    def test_missing_archived_reference_is_not_a_blocker(self):
        self.seed["references"][0]["locator"] = "archive:/not-present/previous-version.py"
        self.assertEqual(module.validate_seed(self.seed, [])["state"], "ready_for_local_probe")

    def test_references_are_never_opened(self):
        original = Path.read_text
        def guarded(path, *args, **kwargs):
            self.assertEqual(path, module.SCHEMA)
            return original(path, *args, **kwargs)
        with patch.object(Path, "read_text", guarded):
            module.validate_seed(self.seed, [])

    def test_required_capability_blocks(self):
        self.seed["requires"] = ["capability:consumer.read"]
        self.assertEqual(module.validate_seed(self.seed, [])["missing_capabilities"], ["capability:consumer.read"])
        self.assertEqual(module.validate_seed(self.seed, [])["state"], "blocked")

    def test_required_capability_present(self):
        self.seed["requires"] = ["capability:consumer.read"]
        self.assertEqual(module.validate_seed(self.seed, ["capability:consumer.read"])["state"], "ready_for_local_probe")

    def test_archive_path_cannot_be_required_capability(self):
        self.seed["requires"] = ["archive/previous.py"]
        self.assertEqual(module.validate_seed(self.seed, [])["state"], "invalid")

    def test_reference_cannot_be_runtime_dependency(self):
        self.seed["references"][0]["use"] = "runtime"
        self.assertEqual(module.validate_seed(self.seed, [])["state"], "invalid")

    def test_reference_cannot_smuggle_block_flag(self):
        self.seed["references"][0]["blocks_completion"] = True
        self.assertEqual(module.validate_seed(self.seed, [])["state"], "invalid")

    def test_missing_acceptance_rejected(self):
        self.seed["acceptance"] = []
        self.assertEqual(module.validate_seed(self.seed, [])["state"], "invalid")

    def test_duplicate_requirements_rejected(self):
        self.seed["requires"] = ["capability:read", "capability:read"]
        self.assertEqual(module.validate_seed(self.seed, [])["state"], "invalid")

    def test_deterministic_and_inputs_unchanged(self):
        before = copy.deepcopy(self.seed)
        self.assertEqual(module.validate_seed(self.seed, []), module.validate_seed(self.seed, []))
        self.assertEqual(self.seed, before)

    def test_availability_must_be_explicit_collection(self):
        with self.assertRaises(ValueError):
            module.validate_seed(self.seed, "capability:read")

if __name__ == "__main__":
    unittest.main()
