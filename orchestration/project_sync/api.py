"""Small injectable GitHub transport. Never retry a mutation blindly."""
import json
import subprocess
import time


class Blocked(RuntimeError):
    def __init__(self, code, operation, detail, retry_after=None):
        self.result = dict(code=code, operation=operation, detail=detail,
                           retry_after=retry_after)
        super().__init__(json.dumps(self.result))


def gh_request(endpoint, payload=None):
    # gh uses its supported credential mechanism; credentials never enter argv.
    command = ["gh", "api", endpoint]
    if payload is not None:
        command += ["--method", "POST", "--input", "-"]
    try:
        proc = subprocess.run(command, input=json.dumps(payload) if payload else None,
                              text=True, capture_output=True, timeout=45)
    except (OSError, subprocess.TimeoutExpired):
        raise Blocked("api_unavailable", endpoint, "CLI unavailable or timed out; re-read before retry") from None
    if proc.returncode:
        # Do not print raw CLI stderr (may include credential/proxy diagnostics).
        text = proc.stderr.lower()
        code = ("rate_limited" if "rate limit" in text or "429" in text else
                "permission_denied" if any(x in text for x in
                    ("401", "403", "scope", "authentication", "token")) else "api_unavailable")
        raise Blocked(code, endpoint, "GitHub CLI request failed; inspect credential permissions")
    try:
        return json.loads(proc.stdout)
    except ValueError:
        raise Blocked("invalid_response", endpoint, "Expected JSON") from None


class API:
    def __init__(self, request=gh_request, sleep=time.sleep):
        self.request, self.sleep = request, sleep

    def call(self, endpoint, payload=None, mutation=False):
        for attempt in range(3):
            try:
                result = self.request(endpoint, payload)
                if isinstance(result, dict) and result.get("errors"):
                    errors = result["errors"]
                    kinds = {e.get("type", "UNKNOWN") for e in errors}
                    code = ("rate_limited" if "RATE_LIMITED" in kinds else
                            "permission_denied" if kinds & {"FORBIDDEN", "UNAUTHORIZED", "INSUFFICIENT_SCOPES"}
                            else "graphql_error")
                    raise Blocked(code, endpoint, "GraphQL returned errors; partial data rejected")
                return result
            except Blocked as exc:
                # Mutation responses can be lost after application. Caller must re-read.
                if mutation or exc.result["code"] != "rate_limited" or attempt == 2:
                    raise
                delay = exc.result.get("retry_after") or 2 ** attempt
                if delay > 30:
                    raise
                self.sleep(delay)

    def rest_pages(self, endpoint, key=None):
        rows = []
        for page in range(1, 1001):
            data = self.call(endpoint + ("&" if "?" in endpoint else "?") +
                             f"per_page=100&page={page}")
            batch = data[key] if key else data
            if not isinstance(batch, list):
                raise Blocked("invalid_response", endpoint, "Expected paginated list")
            rows.extend(batch)
            if len(batch) < 100:
                return rows
        raise Blocked("pagination_limit", endpoint, "Refusing incomplete snapshot")

    def gql(self, query, variables=None, mutation=False):
        return self.call("graphql", dict(query=query, variables=variables or {}), mutation)["data"]

    def connection(self, query, variables, locate):
        rows, seen = [], set()
        variables = dict(variables)
        for _ in range(1000):
            conn = locate(self.gql(query, variables))
            if conn is None:
                raise Blocked("permission_denied", "connection", "Owner or Project not visible")
            rows.extend(conn["nodes"])
            if not conn["pageInfo"]["hasNextPage"]:
                return rows
            cursor = conn["pageInfo"]["endCursor"]
            if not cursor or cursor in seen:
                raise Blocked("pagination_invalid", "connection", "Repeated or missing cursor")
            seen.add(cursor)
            variables["after"] = cursor
        raise Blocked("pagination_limit", "connection", "Refusing incomplete snapshot")


TITLE = "_BASKET — Intelligence & Execution"
STATES = ["BACKLOG", "READY", "CLAIMED", "IN_PROGRESS", "DRAFT_PR", "REVIEW",
          "VALIDATION", "INTEGRATION_VERIFICATION", "COMPLETE", "BLOCKED", "FAILED", "CANCELLED"]
TEXT_FIELDS = ["Domain", "Spark ID", "Worker", "Branch", "Validation", "Acceptance"]
SELECT_FIELDS = {"Status": STATES, "Priority": ["P0", "P1", "P2", "P3"],
                 "Execution Mode": ["Manual", "Codex", "Actions", "Other"]}
PAGE = "pageInfo{hasNextPage endCursor}"


class Project:
    def __init__(self, api, owner="whiterosecoffee", owner_kind="user", apply=False):
        if owner_kind not in ("user", "organization"):
            raise ValueError("owner_kind must be user or organization")
        self.api, self.owner, self.kind, self.apply = api, owner, owner_kind, apply
        self.operations = []

    def discover(self, create=False):
        q = '''query($login:String!,$after:String){OWNER(login:$login){
          id projectsV2(first:100,after:$after){nodes{id title url closed viewerCanUpdate} PAGE}}}'''.replace("OWNER", self.kind).replace("PAGE", PAGE)
        projects = self.api.connection(q, {"login": self.owner}, lambda d: (d[self.kind] or {}).get("projectsV2"))
        matches = [p for p in projects if p["title"] == TITLE and not p["closed"]]
        if len(matches) > 1:
            raise Blocked("ambiguous_project", "discover", "Multiple matching Projects; B00 selection required")
        if matches:
            project = matches[0]
            if self.apply and not project["viewerCanUpdate"]:
                raise Blocked("permission_denied", "updateProjectV2", "Project write permission required")
            return project
        if not create:
            raise Blocked("project_missing", "discover", "No suitable Project found; use --create-project")
        self.operations.append({"operation": "createProjectV2", "title": TITLE})
        if not self.apply:
            return None
        owner = self.api.gql(f'query($login:String!){{{self.kind}(login:$login){{id}}}}', {"login": self.owner})[self.kind]
        if not owner:
            raise Blocked("permission_denied", "createProjectV2", "Owner not visible")
        return self.api.gql('''mutation($owner:ID!,$title:String!){createProjectV2(input:{ownerId:$owner,title:$title}){
          projectV2{id title url closed viewerCanUpdate}}}''', {"owner": owner["id"], "title": TITLE}, True)["createProjectV2"]["projectV2"]

    def fields(self, project):
        q = '''query($id:ID!,$after:String){node(id:$id){... on ProjectV2{fields(first:100,after:$after){
        nodes{... on ProjectV2Field{id name dataType} ... on ProjectV2SingleSelectField{id name dataType options{id name}}
        ... on ProjectV2IterationField{id name dataType}} PAGE}}}}'''.replace("PAGE", PAGE)
        return self.api.connection(q, {"id": project["id"]}, lambda d: (d["node"] or {}).get("fields"))

    def ensure_fields(self, project):
        fields = self.fields(project)
        by_name = {f["name"]: f for f in fields}
        wanted = {**{n: "TEXT" for n in TEXT_FIELDS}, "Last Verified": "DATE",
                  **{n: "SINGLE_SELECT" for n in SELECT_FIELDS}}
        blocked = []
        for name, dtype in wanted.items():
            if name in by_name:
                f = by_name[name]
                missing = set(SELECT_FIELDS.get(name, [])) - {o["name"] for o in f.get("options", [])}
                if f["dataType"] != dtype or missing:
                    # Do not replace existing option IDs or rewrite a live field.
                    blocked.append({"field": name, "reason": "incompatible type or missing options", "missing": sorted(missing)})
                continue
            inp = dict(projectId=project["id"], name=name, dataType=dtype)
            if dtype == "SINGLE_SELECT":
                inp["singleSelectOptions"] = [dict(name=n, color="GRAY", description=n) for n in SELECT_FIELDS[name]]
            self.operations.append({"operation": "createProjectV2Field", "name": name})
            if self.apply:
                self.api.gql('''mutation($input:CreateProjectV2FieldInput!){createProjectV2Field(input:$input){
                  projectV2Field{... on ProjectV2Field{id} ... on ProjectV2SingleSelectField{id}}}}''', {"input": inp}, True)
        return (self.fields(project) if self.apply else fields), blocked

    def items(self, project):
        q = '''query($id:ID!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){nodes{id
          content{... on Issue{id} ... on PullRequest{id}}
          fieldValues(first:100){pageInfo{hasNextPage} nodes{
            ... on ProjectV2ItemFieldTextValue{text field{... on ProjectV2FieldCommon{name}}}
            ... on ProjectV2ItemFieldDateValue{date field{... on ProjectV2FieldCommon{name}}}
            ... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2FieldCommon{name}}}
          }}} PAGE}}}}'''.replace("PAGE", PAGE)
        items = self.api.connection(q, {"id": project["id"]}, lambda d: (d["node"] or {}).get("items"))
        if any(i["fieldValues"]["pageInfo"]["hasNextPage"] for i in items):
            raise Blocked("pagination_limit", "fieldValues", "More than 100 field values; refusing incomplete comparison")
        return items

    def sync(self, project, records, fields):
        items = self.items(project)
        existing = {}
        for item in items:
            content = (item.get("content") or {}).get("id")
            if content in existing:
                raise Blocked("duplicate_project_items", "sync", "Resolve existing duplicate content IDs manually")
            if content:
                existing[content] = item
        available = {f["name"]: f for f in fields}
        failures = []
        for record in records:
            try:
                content = record["node_id"]
                item = existing.get(content)
                if item is None:
                    self.operations.append({"operation": "addProjectV2ItemById", "content": content})
                    if self.apply:
                        item = self.api.gql('''mutation($p:ID!,$c:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$c}){item{id}}}''',
                                            {"p": project["id"], "c": content}, True)["addProjectV2ItemById"]["item"]
                    else:
                        item = {"id": "dry-run:" + content}
                    existing[content] = item
                current = {v["field"]["name"]: v.get("text", v.get("date", v.get("name")))
                           for v in item.get("fieldValues", {}).get("nodes", []) if "field" in v}
                for name, value in record.get("fields", {}).items():
                    if value is None or current.get(name) == value:
                        continue
                    field = available.get(name)
                    if not field:
                        raise Blocked("field_missing", name, "Configure compatible field first")
                    dtype = field["dataType"]
                    if dtype == "SINGLE_SELECT":
                        options = {o["name"]: o["id"] for o in field["options"]}
                        if value not in options:
                            raise Blocked("option_missing", name, "Configure lifecycle options without replacing IDs")
                        inp = {"singleSelectOptionId": options[value]}
                    elif dtype in ("TEXT", "DATE"):
                        inp = {"text" if dtype == "TEXT" else "date": value}
                    else:
                        raise Blocked("unsupported_field", name, "Native relationships must not be copied to text fields")
                    self.operations.append({"operation": "updateProjectV2ItemFieldValue", "content": content, "field": name, "value": value})
                    if self.apply:
                        self.api.gql('''mutation($input:UpdateProjectV2ItemFieldValueInput!){updateProjectV2ItemFieldValue(input:$input){projectV2Item{id}}}''',
                                     {"input": dict(projectId=project["id"], itemId=item["id"], fieldId=field["id"], value=inp)}, True)
                    current[name] = value
                # Update in-memory comparison too for repeated records in the same run.
                item["fieldValues"] = {"nodes": [{"field": {"name": n}, "text": v} for n, v in current.items()]}
            except Blocked as exc:
                failures.append({"content": record.get("node_id"), **exc.result})
                # Any lost mutation response stops this run; re-read all state on retry.
                if exc.result["code"] not in {"field_missing", "option_missing", "unsupported_field"}:
                    break
        return failures
