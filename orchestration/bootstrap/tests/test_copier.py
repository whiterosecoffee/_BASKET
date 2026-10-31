"""Real Copier copy/update integration tests; no mocked template engine or network.

Fixture tags exist only in temporary Git repositories. No repository release tags
are created. Run with the isolated requirements.txt environment.
"""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest

from copier import run_copy, run_update
import yaml

ROOT = Path(__file__).resolve().parents[3]
BOOTSTRAP = ROOT / "orchestration/bootstrap"


def git(directory, *args):
    return subprocess.run(
        ["git", "-c", "user.name=Bootstrap test", "-c", "user.email=bootstrap@example.invalid", *args],
        cwd=directory, text=True, capture_output=True, check=True,
    ).stdout.strip()


class CopierIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "template-source"
        self.source.mkdir()
        shutil.copy(ROOT / "copier.yml", self.source / "copier.yml")
        shutil.copytree(BOOTSTRAP / "template", self.source / "orchestration/bootstrap/template")
        git(self.source, "init", "-b", "main")
        git(self.source, "add", ".")
        git(self.source, "commit", "-m", "Template fixture v1")
        git(self.source, "tag", "v1.0.0")
        self.data = yaml.safe_load((BOOTSTRAP / "basket.yml").read_text())
        self.destination = self.base / "generated"

    def copy(self, destination=None, data=None, **kwargs):
        return run_copy(str(self.source), destination or self.destination,
                        data=data or self.data, defaults=True, vcs_ref="v1.0.0",
                        quiet=True, **kwargs)

    def prepare_update(self):
        self.copy()
        git(self.destination, "init", "-b", "main")
        git(self.destination, "add", ".")
        git(self.destination, "commit", "-m", "Generated baseline")

    def advance_template(self):
        config = self.source / "orchestration/bootstrap/template/.editorconfig"
        config.write_text(config.read_text() + "\n[*.txt]\nindent_size = 2\n")
        git(self.source, "add", ".")
        git(self.source, "commit", "-m", "Template fixture v2")
        git(self.source, "tag", "v1.1.0")

    def test_copy_has_valid_standard_configs_and_git_provenance(self):
        self.copy()
        files = {str(p.relative_to(self.destination)) for p in self.destination.rglob("*") if p.is_file()}
        self.assertEqual(files, {".copier-answers.yml", ".editorconfig", "pyproject.toml",
                                 ".pre-commit-config.yaml", "README.md"})
        answers = yaml.safe_load((self.destination / ".copier-answers.yml").read_text())
        self.assertEqual(answers["_commit"], "v1.0.0")
        self.assertEqual(answers["_src_path"], str(self.source))
        config = tomllib.loads((self.destination / "pyproject.toml").read_text())
        self.assertEqual(config["tool"]["pytest"]["ini_options"]["testpaths"], ["orchestration/project_sync"])
        hooks = yaml.safe_load((self.destination / ".pre-commit-config.yaml").read_text())
        self.assertIn("check-merge-conflict", [h["id"] for h in hooks["repos"][0]["hooks"]])
        self.assertIn("https://github.com/whiterosecoffee/_BASKET", (self.destination / "README.md").read_text())

    def test_same_inputs_render_identical_files(self):
        self.copy()
        other = self.base / "other"
        self.copy(other)
        for original in self.destination.iterdir():
            self.assertEqual(original.read_bytes(), (other / original.name).read_bytes())

    def test_template_is_reusable_for_another_repository(self):
        self.copy(data=dict(project_name="Another Project", repository="example/another",
                            maintainer="example", test_directory="tests/unit"))
        text = (self.destination / "README.md").read_text()
        self.assertIn("example/another", text)
        self.assertNotIn("_BASKET", text)
        config = tomllib.loads((self.destination / "pyproject.toml").read_text())
        self.assertEqual(config["tool"]["pytest"]["ini_options"]["testpaths"], ["tests/unit"])

    def test_update_preserves_local_edits_and_repeated_update_is_noop(self):
        self.prepare_update()
        readme = self.destination / "README.md"
        readme.write_text(readme.read_text() + "\nProject-specific acceptance belongs here.\n")
        git(self.destination, "add", ".")
        git(self.destination, "commit", "-m", "Local project addition")
        self.advance_template()
        run_update(self.destination, defaults=True, vcs_ref="v1.1.0", overwrite=True, quiet=True)
        self.assertIn("Project-specific acceptance belongs here.", readme.read_text())
        self.assertIn("[*.txt]", (self.destination / ".editorconfig").read_text())
        self.assertEqual(yaml.safe_load((self.destination / ".copier-answers.yml").read_text())["_commit"], "v1.1.0")
        git(self.destination, "add", ".")
        git(self.destination, "commit", "-m", "Reviewed fixture update")
        run_update(self.destination, defaults=True, vcs_ref="v1.1.0", overwrite=True, quiet=True)
        self.assertEqual(git(self.destination, "status", "--porcelain"), "")

    def test_invalid_input_is_rejected_before_files_are_published(self):
        for key, value in [("repository", "../other"), ("maintainer", "bad user"),
                           ("test_directory", "../outside"), ("test_directory", "tests; echo unsafe")]:
            with self.subTest(key=key, value=value):
                destination = self.base / ("invalid-" + str(len(list(self.base.iterdir()))))
                with self.assertRaises(ValueError):
                    self.copy(destination, {**self.data, key: value})
                self.assertFalse(destination.exists())

    def test_pretend_does_not_write_destination(self):
        self.copy(pretend=True)
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
