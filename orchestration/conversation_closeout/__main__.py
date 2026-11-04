"""Offline, evidence-supplied conversation closeout audit. Never fetches or mutates GitHub."""
import argparse
import json
from pathlib import Path

DIMENSIONS = ("objective_control", "execution_conversion", "reuse", "ownership_integrity",
              "verification_integrity", "dependency_handling", "resource_efficiency",
              "knowledge_extraction", "handoff_quality", "closure_discipline")
DISPOSITIONS = ("Continue here", "Decision needed", "Hand off before archiving", "Ready to Archive")

def check(ok, message):
    if not ok:
        raise ValueError(message)

def assess(data):
    check(isinstance(data, dict), "input must be an object")
    check(isinstance(data.get("objective"), str) and bool(data["objective"].strip()), "objective required")
    for key in ("local_required_remaining", "decision_required", "external_required_remaining"):
        check(type(data.get(key)) is bool, key + " must be boolean")
    scores = data.get("scores", {})
    check(isinstance(scores, dict) and not set(scores).difference(DIMENSIONS), "invalid score dimensions")
    for key, value in scores.items():
        check(value is None or (type(value) is int and 0 <= value <= 5), "invalid score: " + key)
    count = sum(value is not None for value in scores.values())
    score = round(100 * sum(value for value in scores.values() if value is not None) / (5 * count), 1) if count else None
    disposition = DISPOSITIONS[0 if data["local_required_remaining"] else
                               1 if data["decision_required"] else
                               2 if data["external_required_remaining"] else 3]
    insights = data.get("insights", [])
    check(isinstance(insights, list), "insights must be an array")
    actions = {"already_incorporated", "consolidated", "transfer", "propose", "defer", "discard"}
    for item in insights:
        check(isinstance(item, dict) and isinstance(item.get("principle"), str)
              and bool(item["principle"].strip()), "insight principle required")
        check(item.get("disposition") in actions, "invalid insight disposition")
        check(type(item.get("priority", 0)) is int and 0 <= item.get("priority", 0) <= 25, "invalid insight priority")
    insights = sorted(insights, key=lambda item: (-item.get("priority", 0), item["principle"]))
    handoff = data.get("handoff") if disposition == "Hand off before archiving" else None
    if disposition == "Hand off before archiving":
        check(isinstance(handoff, dict), "handoff required for transfer")
        for key in ("owner", "destination", "objective", "completed", "remaining", "write_paths",
                    "prohibited", "validation", "next_action"):
            check(isinstance(handoff.get(key), str) and bool(handoff[key].strip()), "handoff missing: " + key)
    return {"disposition": disposition, "execution_score": score, "scored_dimensions": count,
            "ranked_insights": insights, "handoff": handoff}

def render(data, result):
    lines = ["# Conversation closeout", "", "**Objective:** " + data["objective"],
             "**Disposition:** " + result["disposition"],
             "**Execution quality:** " + (str(result["execution_score"]) + "/100" if result["execution_score"] is not None else "unverified")
             + " (" + str(result["scored_dimensions"]) + "/10 observed; judgment-based)", "",
             "## Evidence and limits", data.get("evidence", "No evidence supplied; do not claim verification."),
             "", "## Top reusable lessons"]
    for item in result["ranked_insights"][:3]:
        lines.append("- " + item["principle"] + " — " + item["disposition"] +
                     " (priority " + str(item.get("priority", 0)) + "/25)")
    if not result["ranked_insights"]:
        lines.append("No material reusable lesson established.")
    if result["handoff"]:
        h = result["handoff"]
        lines += ["", "## Copyable orchestrator handoff", "```text",
                  "Resume existing work: " + h["objective"], "Owner: " + h["owner"],
                  "Destination: " + h["destination"], "Completed; do not repeat: " + h["completed"],
                  "Remaining acceptance: " + h["remaining"], "Writable paths: " + h["write_paths"],
                  "Prohibited changes: " + h["prohibited"], "Validation and evidence: " + h["validation"],
                  "Recover current authoritative state and ownership before modifying anything.",
                  "Next executable action: " + h["next_action"], "```"]
    return "\n".join(lines + ["", result["disposition"]]) + "\n"

def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline conversation closeout from supplied evidence")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    data = json.loads(args.input.read_text(encoding="utf-8"))
    report = render(data, assess(data))
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")

if __name__ == "__main__":
    main()
