"""Offline consistency checks for operator prompts under orchestration/prompts/<capability>/.

Owner: B00. Stdlib only, no network. Checks structure and internal consistency only;
it does not judge prompt content or market logic.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "orchestration" / "prompts"
DATA_SUFFIXES = {".jsonl", ".csv", ".parquet", ".json.gz"}
LINK = re.compile(r"\]\(([^)#\s]+)\)")


def capability_dirs():
    return sorted(d for d in PROMPTS.iterdir() if d.is_dir()) if PROMPTS.is_dir() else []


def prompt_file(folder):
    files = sorted(folder.glob("*_PROMPT.md"))
    return files[0] if files else None


class OperatorPromptTests(unittest.TestCase):
    def test_each_capability_has_readme_and_prompt(self):
        for d in capability_dirs():
            self.assertTrue((d / "README.md").is_file(), f"{d.name}: README.md missing")
            self.assertIsNotNone(prompt_file(d), f"{d.name}: *_PROMPT.md missing")

    def test_header_declares_capability_version_mode(self):
        for d in capability_dirs():
            head = "\n".join(prompt_file(d).read_text().splitlines()[:6])
            self.assertRegex(head, r"Capability: `basket\.prompt\.[a-z_]+`", d.name)
            self.assertRegex(head, r"version \d+\.\d+\.\d+", d.name)
            self.assertIn("mode: prompt", head, d.name)

    def test_numbered_sections_are_consecutive_from_zero(self):
        for d in capability_dirs():
            nums = [int(n) for n in re.findall(r"^## (\d+)\.", prompt_file(d).read_text(), re.M)]
            self.assertEqual(nums, list(range(len(nums))), d.name)
            self.assertTrue(nums, f"{d.name}: no numbered sections")

    def test_contract_status_set_matches_status_rules(self):
        for d in capability_dirs():
            text = prompt_file(d).read_text()
            contract = re.search(r"status ((?:[A-Z_]+ \| )+[A-Z_]+)", text)
            rules = re.search(r"status of ([A-Z_, ]+(?: or [A-Z_]+))", text)
            self.assertTrue(contract and rules, f"{d.name}: status vocabulary not found")
            a = set(re.findall(r"[A-Z_]{3,}", contract.group(1)))
            b = set(re.findall(r"[A-Z_]{3,}", rules.group(1))) - {"OR"}
            self.assertEqual(a, b, f"{d.name}: contract vs status-rule vocabulary differ")

    def test_relative_links_resolve(self):
        files = [ROOT / "README.md"]
        for d in capability_dirs():
            files += [d / "README.md", prompt_file(d)]
        for f in files:
            for target in LINK.findall(f.read_text()):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                if f.name == "README.md" and f.parent == ROOT and "orchestration/prompts" not in target:
                    continue
                self.assertTrue((f.parent / target).resolve().exists(), f"{f.relative_to(ROOT)} -> {target}")

    def test_no_data_files_under_prompts(self):
        for p in PROMPTS.rglob("*") if PROMPTS.is_dir() else []:
            self.assertNotIn(p.suffix.lower(), DATA_SUFFIXES, f"data file under prompts: {p}")

    def test_readme_states_partition_and_main_wins(self):
        for d in capability_dirs():
            text = (d / "README.md").read_text()
            self.assertIn("Partition and naming", text, d.name)
            self.assertIn("Main wins", text, d.name)
            self.assertIn("Main wins", prompt_file(d).read_text().replace("main wins", "Main wins"), d.name)

    def test_root_readme_points_to_each_capability(self):
        root = (ROOT / "README.md").read_text()
        for d in capability_dirs():
            self.assertIn(f"orchestration/prompts/{d.name}/README.md", root, d.name)


if __name__ == "__main__":
    unittest.main()
