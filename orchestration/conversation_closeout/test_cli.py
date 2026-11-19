"""Exercise the real project command boundary without network or controller state."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from orchestration.conversation_closeout.test_closeout import BASE

ROOT = Path(__file__).resolve().parents[2]
COMMAND = [sys.executable, "-m", "orchestration.agentic.cli"]


class CommandTests(unittest.TestCase):
    def run_command(self, *args):
        return subprocess.run(COMMAND + list(args), cwd=ROOT, capture_output=True,
                              text=True, timeout=10)

    def test_closeout_help_without_controller(self):
        result = self.run_command("closeout", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--input", result.stdout)
        self.assertIn("--output", result.stdout)

    def test_alias_matches_module_stdout_and_file(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "evidence.json"
            output = Path(directory) / "report.md"
            source.write_text(json.dumps(BASE), encoding="utf-8")
            direct = subprocess.run(
                [sys.executable, "-m", "orchestration.conversation_closeout",
                 "--input", str(source)], cwd=ROOT, capture_output=True,
                text=True, timeout=10)
            alias = self.run_command("closeout", "--input", str(source))
            written = self.run_command("closeout", "--input", str(source),
                                       "--output", str(output))
            for result in (direct, alias, written):
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(alias.stdout, direct.stdout)
            self.assertEqual(output.read_text(encoding="utf-8"), direct.stdout)
            self.assertEqual(written.stdout, "")

    def test_invalid_inputs_preserve_output(self):
        handoff = dict(owner="B00", destination="#169", objective="Finish",
                       completed="Tests", remaining="Review", write_paths="orchestration/**",
                       prohibited="Queue", validation="Tests", next_action="Review")
        cases = ["{", "[]", json.dumps(dict(BASE, evidence={})),
                 json.dumps(dict(BASE, decision_required="false")),
                 json.dumps(dict(BASE, scores={"unknown": 3})),
                 json.dumps(dict(BASE, scores={"reuse": True})),
                 json.dumps(dict(BASE, scores={"reuse": 6})),
                 json.dumps(dict(BASE, insights=[dict(principle="x", disposition="unknown")]))]
        for key in handoff:
            incomplete = dict(handoff)
            del incomplete[key]
            cases.append(json.dumps(dict(BASE, external_required_remaining=True,
                                         handoff=incomplete)))
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "evidence.json"
            output = Path(directory) / "report.md"
            for index, raw in enumerate(cases):
                with self.subTest(case=index):
                    source.write_text(raw, encoding="utf-8")
                    output.write_text("sentinel", encoding="utf-8")
                    result = self.run_command("closeout", "--input", str(source),
                                              "--output", str(output))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")
                    self.assertEqual(output.read_text(encoding="utf-8"), "sentinel")

    def test_missing_arguments_fail(self):
        self.assertEqual(self.run_command("closeout").returncode, 2)

    def test_existing_cli_help_and_required_arguments(self):
        help_result = self.run_command("--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("closeout", help_result.stdout)
        self.assertIn("--queue", help_result.stdout)
        missing = self.run_command()
        self.assertEqual(missing.returncode, 2)
        self.assertIn("--queue", missing.stderr)


if __name__ == "__main__":
    unittest.main()
