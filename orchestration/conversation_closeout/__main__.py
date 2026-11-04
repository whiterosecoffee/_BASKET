"""Offline, evidence-supplied conversation closeout audit. Never fetches or mutates GitHub."""
import argparse
import json
from pathlib import Path

DIMENSIONS = ("objective_control", "execution_conversion", "reuse", "ownership_integrity",
              "verification_integrity", "dependency_handling", "resource_efficiency",
              "knowledge_extraction", "handoff_quality", "closure_discipline")
THEORY_TAGS = {
    "DBC": "Design by Contract", "HEX": "Ports and adapters",
    "DAG": "Dependency graphs", "EVS": "Event sourcing",
    "CQRS": "Command/query separation", "IDEM": "Idempotency",
    "PIT": "Point-in-time validity", "PROV": "Provenance",
    "FALS": "Falsification", "REPRO": "Reproducibility",
    "FSM": "State machines", "POST": "Postmortem learning",
    "INFO": "Information compression", "DEC": "Decision theory",
    "MOD": "Modularity", "OBS": "Observability",
}
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
    claims = data.get("claims", [])
    check(isinstance(claims, list), "claims must be an array")
    claim_ids = set()
    allowed_claim_types = {"user_assertion", "conversation_observation", "repository_verified",
                           "independent_test", "inference", "proposal", "unknown"}
    for claim in claims:
        check(isinstance(claim, dict), "claim must be an object")
        cid = claim.get("id")
        check(isinstance(cid, str) and bool(cid.strip()) and cid not in claim_ids,
              "claim ID missing or duplicated")
        claim_ids.add(cid)
        check(claim.get("type") in allowed_claim_types, "invalid claim type")
        check(isinstance(claim.get("text"), str) and bool(claim["text"].strip()),
              "claim text required")
        if claim["type"] in {"repository_verified", "independent_test"}:
            check(isinstance(claim.get("source_ref"), str) and bool(claim["source_ref"].strip())
                  and isinstance(claim.get("revision"), str) and bool(claim["revision"].strip()),
                  "verified claim requires source_ref and revision")
    insights = data.get("insights", [])
    check(isinstance(insights, list), "insights must be an array")
    actions = {"already_incorporated", "consolidated", "transfer", "propose", "defer", "discard"}
    for item in insights:
        check(isinstance(item, dict) and isinstance(item.get("principle"), str)
              and bool(item["principle"].strip()), "insight principle required")
        check(item.get("disposition") in actions, "invalid insight disposition")
        for field in ("pattern", "methodology", "application", "evidence", "limitations",
                      "architecture", "capability_match", "rationale"):
            if field in item:
                check(isinstance(item[field], str), "invalid insight field: " + field)
        if "theory_tags" in item:
            tags = item["theory_tags"]
            check(isinstance(tags, list) and
                  all(isinstance(tag, str) and bool(tag.strip()) for tag in tags)
                  and len(tags) == len(set(tags)), "invalid theory_tags")
        if "architectural" in item:
            check(type(item["architectural"]) is bool, "architectural must be boolean")
        if "prior_art" in item:
            check(isinstance(item["prior_art"], list), "prior_art must be an array")
            for pointer in item["prior_art"]:
                check(isinstance(pointer, dict), "prior_art pointer must be an object")
                for field in ("family", "mechanism", "applicability", "boundary"):
                    check(isinstance(pointer.get(field), str) and bool(pointer[field].strip()),
                          "prior_art pointer missing: " + field)
                if "reference" in pointer:
                    check(isinstance(pointer["reference"], str), "prior_art reference must be text")
        if "claim_ids" in item:
            check(isinstance(item["claim_ids"], list) and
                  all(isinstance(cid, str) and cid in claim_ids for cid in item["claim_ids"]),
                  "insight references unknown claim")
        check(type(item.get("priority", 0)) is int and 0 <= item.get("priority", 0) <= 25, "invalid insight priority")
    insights = sorted(insights, key=lambda item: (-item.get("priority", 0), item["principle"]))
    taxonomy_gaps = []
    for item in insights:
        if item.get("architectural") and not item.get("theory_tags"):
            taxonomy_gaps.append({"principle": item["principle"], "tag": None,
                                  "reason": "architectural insight lacks theory classification"})
        for tag in item.get("theory_tags", []):
            if tag not in THEORY_TAGS:
                taxonomy_gaps.append({"principle": item["principle"], "tag": tag,
                                      "reason": "unrecognized theory family; owner review required"})
    handoff = data.get("handoff") if disposition == "Hand off before archiving" else None
    if disposition == "Hand off before archiving":
        check(isinstance(handoff, dict), "handoff required for transfer")
        for key in ("owner", "destination", "objective", "completed", "remaining", "write_paths",
                    "prohibited", "validation", "next_action"):
            check(isinstance(handoff.get(key), str) and bool(handoff[key].strip()), "handoff missing: " + key)
    return {"disposition": disposition, "execution_score": score, "scored_dimensions": count,
            "claims": claims,
            "ranked_insights": insights, "taxonomy_gaps": taxonomy_gaps, "handoff": handoff}

def render(data, result):
    lines = ["# Conversation closeout", "", "**Objective:** " + data["objective"],
             "**Disposition:** " + result["disposition"],
             "**Execution quality:** " + (str(result["execution_score"]) + "/100" if result["execution_score"] is not None else "unverified")
             + " (" + str(result["scored_dimensions"]) + "/10 observed; judgment-based)", "",
             "## Evidence and limits", data.get("evidence", "No evidence supplied; do not claim verification."),
             "", "## Top reusable lessons"]
    for index, item in enumerate(result["ranked_insights"]):
        if index == 3:
            lines += ["", "## Additional retained knowledge"]
        lines.append("- " + item["principle"] + " — " + item["disposition"] +
                     " (priority " + str(item.get("priority", 0)) + "/25)")
        for field in ("pattern", "methodology", "application", "evidence", "limitations",
                      "architecture", "capability_match", "rationale"):
            if item.get(field):
                lines.append("  - " + field.replace("_", " ").title() + ": " + item[field])
        if item.get("theory_tags"):
            lines.append("  - Theory: " + " · ".join(
                tag + " (" + THEORY_TAGS.get(tag, "unclassified — review") + ")" for tag in item["theory_tags"]))
        for pointer in item.get("prior_art", []):
            lines.append("  - Prior art: " + pointer["family"] + " — " + pointer["mechanism"] +
                         "; applies: " + pointer["applicability"] +
                         "; boundary: " + pointer["boundary"] +
                         ("; reference: " + pointer["reference"] if pointer.get("reference") else ""))
    if not result["ranked_insights"]:
        lines.append("No material reusable lesson established.")
    if result["taxonomy_gaps"]:
        lines += ["", "## Taxonomy review required"]
        for gap in result["taxonomy_gaps"]:
            lines.append("- " + gap["principle"] + ": " +
                         (gap["tag"] if gap["tag"] else "missing classification") +
                         " — " + gap["reason"])
    if result["claims"]:
        lines += ["", "## Claim provenance"]
        for claim in result["claims"]:
            lines.append("- " + claim["id"] + " [" + claim["type"] + "]: " + claim["text"] +
                         (" (" + claim["source_ref"] + " @ " + claim["revision"] + ")"
                          if claim.get("source_ref") and claim.get("revision") else ""))
    if result["handoff"]:
        h = result["handoff"]
        lines += ["", "## Copyable orchestrator handoff", "```text",
                  "Resume existing work: " + h["objective"], "Owner: " + h["owner"],
                  "Conversation objective and requirements: " + data["objective"],
                  "Evidence and limits: " + data.get("evidence", "No evidence supplied; do not claim verification."),
                  "Destination: " + h["destination"], "Completed; do not repeat: " + h["completed"],
                  "Remaining acceptance: " + h["remaining"], "Writable paths: " + h["write_paths"],
                  "Prohibited changes: " + h["prohibited"], "Validation and evidence: " + h["validation"],
                  "Knowledge to preserve: " + "; ".join(
                      item["principle"] + " [" + item["disposition"] + "]" +
                      (" — " + item.get("rationale", "") if item.get("rationale") else "")
                      + (" | pattern: " + item["pattern"] if item.get("pattern") else "")
                      + (" | architecture: " + item["architecture"] if item.get("architecture") else "")
                      + (" | destination: " + item["capability_match"] if item.get("capability_match") else "")
                      + (" | evidence: " + item["evidence"] if item.get("evidence") else "")
                      + (" | claims: " + ",".join(item["claim_ids"]) if item.get("claim_ids") else "")
                      + (" | method: " + item["methodology"] if item.get("methodology") else "")
                      + (" | applies: " + item["application"] if item.get("application") else "")
                      + (" | boundary: " + item["limitations"] if item.get("limitations") else "")
                      + (" | theory: " + ",".join(item["theory_tags"]) if item.get("theory_tags") else "")
                      + (" | prior art: " + "; ".join(
                          p["family"] + " (" + p["mechanism"] + "; applies: " + p["applicability"]
                          + "; boundary: " + p["boundary"]
                          + ("; reference: " + p["reference"] if p.get("reference") else "") + ")"
                          for p in item.get("prior_art", [])) if item.get("prior_art") else "")
                      for item in result["ranked_insights"]),
                  "Claim provenance: " + "; ".join(
                      claim["id"] + " [" + claim["type"] + "]: " + claim["text"]
                      + (" (" + claim["source_ref"] + " @ " + claim["revision"] + ")"
                         if claim.get("source_ref") and claim.get("revision") else "")
                      for claim in result["claims"]),
                  "Taxonomy gaps to review: " + "; ".join(
                      gap["principle"] + " (" + (gap["tag"] or "unclassified") + ")"
                      for gap in result["taxonomy_gaps"]),
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

