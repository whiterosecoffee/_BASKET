#!/usr/bin/env python3
"""Fail-closed worker scope compiler/validator; profiles never grant write access."""
import json
from pathlib import Path
from fnmatch import fnmatchcase
ROOT=Path(__file__).resolve().parents[1]
def read(relative): return json.loads((ROOT/relative).read_text(encoding="utf-8"))
def within(scope,allowed):
    if scope==allowed:return True
    if "*" not in scope:return fnmatchcase(scope,allowed) and (allowed.endswith("/**") or scope.count("/")==allowed.count("/"))
    return scope.endswith("/**") and allowed.endswith("/**") and scope.startswith(allowed[:-2])
def validate(reg,queue,library,compiled):
    errors=[]
    sparks={s["id"]:s for s in reg["sparks"]}
    tasks={t["id"]:t for t in queue["tasks"]}
    recipes={r["id"]:r for r in library["recipes"]}
    scopes=compiled["scopes"]
    if len(scopes)!=len(tasks) or len({x["task_id"] for x in scopes})!=len(scopes):errors.append("missing or duplicate scope")
    if compiled["source_queue_version"]!=queue["queue_version"]:errors.append("queue version mismatch")
    if compiled["source_spark_catalog_version"]!=reg["catalog_version"]:errors.append("catalog version mismatch")
    for s in scopes:
        t=tasks.get(s["task_id"])
        if t is None:errors.append("unknown task "+s["task_id"]);continue
        owner=sparks[t["spark_id"]]
        if s["spark_id"]!=owner["id"] or s["objective"]!=t["objective"] or s["mode"]!=t["mode"]:errors.append("task identity mismatch "+t["id"])
        if s["owner_issue"]!=t["issue_number"] or s["existing_pr"]!=t["pr_number"]:errors.append("worker issue mismatch "+t["id"])
        if s["dependencies"]!=t["depends_on"] or s["acceptance"]!=t["acceptance"]:errors.append("dependencies/acceptance mismatch "+t["id"])
        expected=t["write_scope"] or owner["write_paths"]
        if s["exclusive_write_paths"]!=expected:errors.append("scope paths mismatch "+t["id"])
        for path in s["exclusive_write_paths"]:
            if not any(within(path,a) for a in owner["write_paths"]):errors.append("out of domain "+t["id"]+":"+path)
        recipe=recipes[t["recipe"]]["steps"]
        if len(s["steps"])!=len(recipe):errors.append("recipe length mismatch "+t["id"])
        for i,step in enumerate(s["steps"]):
            if i>=len(recipe):break
            if step["step_id"]!=f'{t["id"]}-S{i+1}' or step["capability"]!=recipe[i]["capability"] or step["deliverable"]!=recipe[i]["output"]:errors.append("recipe mismatch "+t["id"])
    return errors
def main():
    errors=validate(read("orchestration/sparks.json"),read("orchestration/planner/queue.json"),read("orchestration/planner/worker-library.json"),read("orchestration/planner/worker-scopes.json"))
    print(json.dumps({"status":"fail" if errors else "pass","errors":errors,"note":"static validation only"}))
    return bool(errors)
if __name__=="__main__":raise SystemExit(main())
