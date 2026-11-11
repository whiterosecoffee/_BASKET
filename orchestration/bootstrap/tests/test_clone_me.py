"""Real generated CLI, schema, consumer and update acceptance."""
import json
import subprocess
import sys
import unittest
from jsonschema import Draft202012Validator
from copier import run_update
from test_copier import CopierIntegrationTests as Base, git


class CloneMeTests(unittest.TestCase):
    setUp = Base.setUp
    copy = Base.copy
    prepare_update = Base.prepare_update
    advance_template = Base.advance_template

    def test_generate_run_consume_validate_and_replay(self):
        self.copy(data={**self.data, "include_component": True})
        request = self.destination / "clone_me/request.json"
        before = request.read_bytes()
        command = [sys.executable, "-m", "clone_me.component", str(request)]
        first = subprocess.run(command, cwd=self.destination, capture_output=True, text=True, check=True)
        second = subprocess.run(command, cwd=self.destination, capture_output=True, text=True, check=True)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(request.read_bytes(), before)
        result = json.loads(first.stdout)
        self.assertEqual(result, {"request_id": "smoke-1", "status": "ok", "payload": {}})
        for name, instance in [("request", json.loads(before)), ("result", result)]:
            schema = json.loads((self.destination / f"clone_me/{name}.schema.json").read_text())
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema).validate(instance)
        tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "clone_me", "-p", "test_*.py", "-v"], cwd=self.destination, text=True, capture_output=True, check=True)
        self.assertIn("Ran 2 tests", tests.stderr)
        handoff = (self.destination / "clone_me/HANDOFF.md").read_text()
        for value in ["https://github.com/whiterosecoffee/_BASKET", "Canonical issue URL: UNASSIGNED", "basket.worker_task@1", "basket.worker_resolution@1"]:
            self.assertIn(value, handoff)

    def test_bad_json_and_invalid_payload_fail_without_success(self):
        self.copy(data={**self.data, "include_component": True})
        request = self.base / "invalid.json"
        for text in ['not json', '{"request_id":"x","payload":{"invented":1}}', '{"request_id":"x","request_id":"y","payload":{}}']:
            request.write_text(text)
            result = subprocess.run([sys.executable, "-m", "clone_me.component", str(request)], cwd=self.destination, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertEqual(request.read_text(), text)

    def test_deterministic_other_repository(self):
        data = dict(project_name="Another Project", repository="example/another", maintainer="example", test_directory="tests", include_component=True)
        self.copy(data=data)
        other = self.base / "other-clone"
        self.copy(other, data=data)
        for original in self.destination.rglob("*"):
            if original.is_file():
                self.assertEqual(original.read_bytes(), (other / original.relative_to(self.destination)).read_bytes())
        self.assertIn("example/another", (other / "clone_me/HANDOFF.md").read_text())

    def test_update_retains_owner_edits_and_repeats_without_change(self):
        self.data["include_component"] = True
        self.prepare_update()
        source = self.destination / "clone_me/component.py"
        source.write_text(source.read_text() + "\n# Receiving owner local extension.\n")
        git(self.destination, "add", ".")
        git(self.destination, "commit", "-m", "Receiver local extension")
        upstream = self.source / "orchestration/bootstrap/template/{% if include_component %}clone_me{% endif %}/component.py"
        upstream.write_text("# Reviewed template extension.\n" + upstream.read_text())
        self.advance_template()
        run_update(self.destination, defaults=True, vcs_ref="v1.1.0", overwrite=True, quiet=True)
        self.assertIn("# Receiving owner local extension.", source.read_text())
        self.assertIn("# Reviewed template extension.", source.read_text())
        git(self.destination, "add", ".")
        git(self.destination, "commit", "-m", "Template update")
        run_update(self.destination, defaults=True, vcs_ref="v1.1.0", overwrite=True, quiet=True)
        self.assertEqual(git(self.destination, "status", "--porcelain"), "")

# Do not rediscover imported baseline tests.
del Base
