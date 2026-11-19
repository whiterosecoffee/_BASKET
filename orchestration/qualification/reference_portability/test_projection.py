import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

projection = load("project_references")
audit = load("audit").audit


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payload = b'{"value":7}\n'
        (self.root / "payload.json").write_bytes(self.payload)
        self.mapping = {"sources": {"payload.json": {
            "path": "payload.json", "commit": "a"*40,
            "sha256": hashlib.sha256(self.payload).hexdigest(),
            "url": "https://example.invalid/payload.json", "state": "draft_unmerged"},
            "unselected": {"not": "a required input"}}}
        self.seed = {"schema": "basket.clean_seed@1", "references": [
            {"locator": "https://example.invalid/archived", "use": "reference_only"}],
            "requires": [{"capability": "synthetic.unavailable"}]}

    def run_audit(self, document):
        (self.root / "entry.json").write_text(json.dumps(document))
        return audit(self.root, "entry.json")

    def test_map_composes_with_audit(self):
        result = self.run_audit(projection.map_sources(self.mapping, ["payload.json"]))
        self.assertTrue(result["ok"])
        self.assertEqual(result["references"][0]["sha256"], hashlib.sha256(self.payload).hexdigest())

    def test_map_missing_required_rejects(self):
        document = projection.map_sources(self.mapping, ["payload.json"])
        (self.root / "payload.json").unlink()
        self.assertFalse(self.run_audit(document)["ok"])

    def test_map_wrong_hash_rejects(self):
        self.mapping["sources"]["payload.json"]["sha256"] = "0"*64
        self.assertFalse(self.run_audit(projection.map_sources(self.mapping, ["payload.json"]))["ok"])

    def test_unknown_empty_duplicate_selection_rejects(self):
        for selected in ([], ["unknown"], ["payload.json", "payload.json"], [None]):
            with self.subTest(selected=selected), self.assertRaises(projection.ProjectionError):
                projection.map_sources(self.mapping, selected)

    def test_missing_malformed_pins_reject(self):
        for field, value in (("sha256", None), ("sha256", "bad"), ("commit", "main"), ("path", "different.json")):
            candidate = copy.deepcopy(self.mapping)
            candidate["sources"]["payload.json"][field] = value
            with self.subTest(field=field,value=value), self.assertRaises(projection.ProjectionError):
                projection.map_sources(candidate, ["payload.json"])

    def test_unsafe_selected_paths_reject(self):
        for path in ("../payload.json", "/payload.json", "C:/payload.json", "a\\b.json", "a//b.json", "a/./b.json", "code.py"):
            source = copy.deepcopy(self.mapping["sources"]["payload.json"])
            source["path"] = path
            with self.subTest(path=path), self.assertRaises(projection.ProjectionError):
                projection.map_sources({"sources":{path:source}}, [path])

    def test_seed_urls_are_notes_not_required_paths(self):
        projected = projection.seed_references(self.seed)
        self.assertEqual(projected["references"], [])
        self.assertEqual(projected["projection"]["reference_notes"][0]["locator"], self.seed["references"][0]["locator"])
        result = self.run_audit(projected)
        self.assertTrue(result["ok"])
        self.assertEqual(result["references"], [])
        self.assertEqual(len(result["files"]), 1)

    def test_seed_capabilities_remain_explicitly_unevaluated(self):
        projected = projection.seed_references(self.seed)
        self.assertEqual(projected["projection"]["capability_evaluation"], "not_performed")
        self.assertEqual(projected["projection"]["required_capabilities"], self.seed["requires"])
        self.assertEqual(projected["projection"]["audit_scope"], "informational_only")
        projected["projection"]["required_capabilities"][0]["capability"] = "changed"
        self.assertEqual(self.seed["requires"][0]["capability"], "synthetic.unavailable")

    def test_seed_required_or_unknown_reference_use_rejects(self):
        for use in ("required", "archive", None):
            candidate = copy.deepcopy(self.seed)
            candidate["references"][0]["use"] = use
            with self.subTest(use=use), self.assertRaises(projection.ProjectionError):
                projection.seed_references(candidate)

    def test_projection_deterministic_and_inputs_unchanged(self):
        before = copy.deepcopy((self.mapping, self.seed))
        for _ in range(2):
            self.assertEqual(projection.map_sources(self.mapping, ["payload.json"]), projection.map_sources(self.mapping, ["payload.json"]))
            self.assertEqual(projection.seed_references(self.seed), projection.seed_references(self.seed))
        self.assertEqual((self.mapping, self.seed), before)
        self.assertEqual((self.root / "payload.json").read_bytes(), self.payload)

    def test_map_provenance_does_not_claim_commit_verification(self):
        result = projection.map_sources(self.mapping, ["payload.json"])
        self.assertEqual(result["projection"]["commit_verification"], "not_performed")
        self.assertEqual(result["projection"]["selected_source_provenance"][0]["commit"], "a"*40)

    def test_cli_success_failure_and_duplicate_keys(self):
        doc = self.root / "source.json"
        cmd = [sys.executable, "-B", str(HERE / "project_references.py"), "--document", str(doc)]
        doc.write_text(json.dumps(self.mapping))
        good = subprocess.run(cmd+["--profile","map","--select","payload.json"],capture_output=True,text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)["references"][0]["ref"], "payload.json")
        bad = subprocess.run(cmd+["--profile","map"],capture_output=True,text=True)
        self.assertEqual(bad.returncode, 1)
        doc.write_text('{"sources":{},"sources":{}}')
        bad = subprocess.run(cmd+["--profile","map","--select","payload.json"],capture_output=True,text=True)
        self.assertEqual(bad.returncode, 1)


if __name__ == "__main__":
    unittest.main()
