"""Explicit existing-Project selection; all API calls are stateful doubles."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from api import API, Blocked, Project, TITLE
from control import main
import test_sync as support


class ExplicitGitHub(support.FakeGitHub):
    def __init__(self, owner="whiterosecoffee", kind="user"):
        super().__init__()
        self.owner, self.kind = owner, kind
        self.board.update(id="P2", number=2, title="_Basket",
                          url=f"https://github.com/users/{owner}/projects/2")
        self.projects = [dict(self.board, id="P1", number=1, title=TITLE), self.board]
        self.owner_lookups = []

    def __call__(self, endpoint, payload):
        query, variables = payload["query"], payload["variables"]
        if "projectsV2(" in query:
            self.queries.append(query)
            self.owner_lookups.append(variables["login"])
            assert f"{self.kind}(login:" in query
            assert "number" in query
            return {"data": {self.kind: {"projectsV2": support.connection(
                self.projects if variables["login"] == self.owner else [])}}}
        return super().__call__(endpoint, payload)


class SelectionTests(unittest.TestCase):
    def assert_blocked(self, fake, code, **kwargs):
        project = Project(API(fake), apply=True, **kwargs)
        with self.assertRaises(Blocked) as ctx:
            project.discover()
        self.assertEqual(ctx.exception.result["code"], code)
        self.assertEqual(fake.writes, [])
        self.assertEqual(project.operations, [])

    def test_number_selects_existing_board_with_different_title(self):
        fake = ExplicitGitHub()
        self.assertEqual(Project(API(fake), project_number=2).discover()["id"], "P2")
        self.assertEqual(fake.writes, [])

    def test_id_selects_existing_board_with_different_title(self):
        fake = ExplicitGitHub()
        self.assertEqual(Project(API(fake), project_id="P2").discover()["number"], 2)
        self.assertEqual(fake.writes, [])

    def test_rename_does_not_change_selection(self):
        fake = ExplicitGitHub()
        fake.board["title"] = "Renamed by owner"
        for selector in ({"project_number": 2}, {"project_id": "P2"}):
            self.assertEqual(Project(API(fake), **selector).discover()["id"], "P2")

    def test_missing_target_never_falls_back_to_default_title(self):
        for selector in ({"project_number": 3}, {"project_id": "OTHER"}):
            self.assert_blocked(ExplicitGitHub(), "project_missing", **selector)

    def test_closed_target_never_falls_back(self):
        fake = ExplicitGitHub()
        fake.board["closed"] = True
        self.assert_blocked(fake, "project_closed_or_unverified", project_number=2)

    def test_unknown_closed_state_blocks(self):
        fake = ExplicitGitHub()
        del fake.board["closed"]
        self.assert_blocked(fake, "project_closed_or_unverified", project_id="P2")

    def test_number_requires_native_id(self):
        fake = ExplicitGitHub()
        del fake.board["id"]
        self.assert_blocked(fake, "invalid_response", project_number=2)

    def test_duplicate_number_blocks_even_if_one_is_closed(self):
        fake = ExplicitGitHub()
        fake.projects.append(dict(fake.board, id="OTHER", closed=True))
        self.assert_blocked(fake, "ambiguous_project", project_number=2)

    def test_duplicate_id_blocks(self):
        fake = ExplicitGitHub()
        fake.projects.append(copy.deepcopy(fake.board))
        self.assert_blocked(fake, "ambiguous_project", project_id="P2")

    def test_foreign_owner_target_is_not_selected_by_id(self):
        self.assert_blocked(ExplicitGitHub(), "project_missing", owner="another-owner", project_id="P2")

    def test_organization_selection_is_owner_scoped(self):
        fake = ExplicitGitHub(owner="example-org", kind="organization")
        board = Project(API(fake), owner="example-org", owner_kind="organization", project_number=2).discover()
        self.assertEqual(board["id"], "P2")
        self.assertEqual(fake.owner_lookups, ["example-org"])

    def test_read_only_permission_is_sufficient_for_dry_run(self):
        fake = ExplicitGitHub()
        fake.board["viewerCanUpdate"] = False
        self.assertEqual(Project(API(fake), project_number=2).discover()["id"], "P2")
        self.assertEqual(fake.writes, [])

    def test_missing_or_denied_update_permission_blocks_apply(self):
        for value in (False, None, "true", 1):
            fake = ExplicitGitHub()
            fake.board["viewerCanUpdate"] = value
            self.assert_blocked(fake, "permission_denied", project_number=2)

    def test_selector_cannot_create_even_when_target_exists(self):
        for selector in ({"project_number": 2}, {"project_id": "P2"}):
            fake = ExplicitGitHub()
            project = Project(API(fake), apply=True, **selector)
            with self.assertRaisesRegex(Blocked, "invalid_project_selection"):
                project.discover(create=True)
            self.assertEqual(fake.queries, [])
            self.assertEqual(fake.writes, [])
            self.assertEqual(project.operations, [])

    def test_invalid_selector_values_rejected_before_api(self):
        values = [{"project_number": v} for v in (0, -1, True, 2.0, "2")]
        values += [{"project_id": v} for v in ("", " P2", "P2\n", 2, True)]
        values += [{"project_number": 2, "project_id": "P2"}]
        for selector in values:
            fake = ExplicitGitHub()
            with self.subTest(selector=selector), self.assertRaises(ValueError):
                Project(API(fake), **selector)
            self.assertEqual(fake.queries, [])

    def test_target_on_later_page_is_selected(self):
        calls = []
        def request(endpoint, payload):
            variables = payload["variables"]
            calls.append(variables.copy())
            later = "after" in variables
            boards = [dict(id="P2", number=2, title="_Basket", closed=False, viewerCanUpdate=True)] if later else []
            return {"data": {"user": {"projectsV2": support.connection(boards, not later, "next")}}}
        self.assertEqual(Project(API(request), project_number=2).discover()["id"], "P2")
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1]["after"], "next")

    def test_partial_error_never_selects_visible_target(self):
        api = API(lambda *a: {"data": {"user": {"projectsV2": support.connection([])}},
                              "errors": [{"type": "FORBIDDEN"}]})
        with self.assertRaisesRegex(Blocked, "permission_denied"):
            Project(api, project_number=2).discover()

    def test_target_on_first_page_cannot_hide_later_page_failure(self):
        for failure in ("permission_denied", "pagination_invalid"):
            calls = []
            def request(endpoint, payload):
                self.assertFalse(payload["query"].startswith("mutation"))
                later = bool(calls)
                calls.append(payload)
                if later and failure == "permission_denied":
                    return {"errors": [{"type": "FORBIDDEN"}]}
                return {"data": {"user": {"projectsV2": support.connection(
                    [ExplicitGitHub().board] if not later else [], True, "same")}}}
            project = Project(API(request), apply=True, project_number=2)
            with self.subTest(failure=failure), self.assertRaisesRegex(Blocked, failure):
                project.discover()
            self.assertEqual(len(calls), 2)
            self.assertEqual(project.operations, [])

    def test_duplicate_target_across_pages_blocks(self):
        calls = []
        def request(endpoint, payload):
            self.assertFalse(payload["query"].startswith("mutation"))
            later = bool(calls)
            calls.append(payload)
            return {"data": {"user": {"projectsV2": support.connection(
                [ExplicitGitHub().board], not later, "next")}}}
        project = Project(API(request), apply=True, project_number=2)
        with self.assertRaisesRegex(Blocked, "ambiguous_project"):
            project.discover()
        self.assertEqual(project.operations, [])

    def test_inaccessible_owner_is_structured_block(self):
        api = API(lambda *a: {"data": {"user": None}})
        project = Project(api, apply=True, project_id="P2")
        with self.assertRaisesRegex(Blocked, "permission_denied"):
            project.discover()
        self.assertEqual(project.operations, [])

    def test_default_title_behavior_unchanged(self):
        fake = ExplicitGitHub()
        self.assertEqual(Project(API(fake)).discover()["id"], "P1")
        fake.projects.append(dict(fake.projects[0], id="duplicate"))
        self.assert_blocked(fake, "ambiguous_project")


class SelectionCLITests(unittest.TestCase):
    def run_cli(self, fake, *arguments):
        case = support.GateTests()
        case.setUp()
        with tempfile.TemporaryDirectory() as directory, \
                patch("control.collect", return_value=case.snapshot), \
                patch("control.API", return_value=API(fake)), patch("builtins.print"):
            output = Path(directory) / "report.json"
            with patch("sys.argv", ["control", *arguments, "--report", str(output)]):
                result = main()
            return result, json.loads(output.read_text())

    def test_dry_run_selects_project_2_and_never_writes(self):
        fake = ExplicitGitHub()
        result, report = self.run_cli(fake, "--project-number", "2")
        self.assertEqual(result, 0)
        self.assertEqual(report["project"]["id"], "P2")
        self.assertEqual(fake.writes, [])

    def test_id_cli_selects_project_2(self):
        result, report = self.run_cli(ExplicitGitHub(), "--project-id", "P2")
        self.assertEqual(result, 0)
        self.assertEqual(report["project"]["number"], 2)

    def test_missing_target_blocks_all_configuration_and_imports(self):
        fake = ExplicitGitHub()
        result, report = self.run_cli(fake, "--apply", "--project-number", "3")
        self.assertEqual(result, 2)
        self.assertEqual(report["blocked"][0]["code"], "project_missing")
        self.assertEqual(fake.writes, [])
        self.assertEqual(report["operations"], [])

    def test_native_status_repeat_apply_is_idempotent_on_selected_project(self):
        fake = ExplicitGitHub()
        fake.fields[0]["options"] = [{"id": "native-" + name, "name": name}
                                      for name in ("Todo", "In Progress", "Done")]
        args = ("--apply", "--native-status", "--project-number", "2")
        self.assertEqual(self.run_cli(fake, *args)[0], 0)
        writes = len(fake.writes)
        self.assertGreater(writes, 0)
        for payload in fake.writes:
            variables = payload["variables"]
            self.assertEqual(variables.get("input", {}).get("projectId", variables.get("p")), "P2")
        self.assertEqual(self.run_cli(fake, *args)[0], 0)
        self.assertEqual(len(fake.writes), writes)

    def test_cli_invalid_or_conflicting_selection_fails_before_collection(self):
        cases = [("--project-number", "2", "--create-project"),
                 ("--project-id", "P2", "--create-project"),
                 ("--project-number", "2", "--project-id", "P2"),
                 ("--project-number", "0"), ("--project-number", "-1"),
                 ("--project-number", "abc"), ("--project-id", ""),
                 ("--project-id", "P2 ")]
        for args in cases:
            with self.subTest(args=args), patch("control.collect") as collect, \
                    patch("control.API") as api, patch("sys.stderr", new_callable=io.StringIO), \
                    patch("sys.argv", ["control", *args, "--report", "unused.json"]):
                with self.assertRaises(SystemExit) as ctx:
                    main()
                self.assertEqual(ctx.exception.code, 2)
                collect.assert_not_called()
                api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
