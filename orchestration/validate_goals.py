#!/usr/bin/env python3
"""Validate desired goals/milestones against versioned schema and live task definitions.

This checks a PLAN, not live worker completion. Run:
  python orchestration/validate_goals.py
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]
def load(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))
def validate(goals,queue):
 errors=[]
 task_ids={t["id"] for t in queue["tasks"]}
 gids=[g["id"] for g in goals["goals"]]
 mids=[m["id"] for m in goals["milestones"]]
 if len(set(gids))!=len(gids): errors.append("duplicate goal IDs")
 if len(set(mids))!=len(mids): errors.append("duplicate milestone IDs")
 if goals["execution_policy"]["active_code_writers_limit"]!=queue["active_worker_limit"]:
  errors.append("worker capacity policy drift")
 covered=set()
 byid={m["id"]:m for m in goals["milestones"]}
 for m in goals["milestones"]:
  if m["goal_id"] not in gids:errors.append("unknown goal "+m["goal_id"])
  for tid in m["task_ids"]:
   if tid not in task_ids:errors.append("unknown queue task "+tid)
   if tid in covered:errors.append("task belongs to multiple milestone goals: "+tid)
   covered.add(tid)
  for dep in m["depends_on"]:
   if dep not in byid:errors.append("unknown milestone dependency: "+dep)
   if dep==m["id"]:errors.append("self milestone dependency "+dep)
 missing=task_ids-covered
 if missing:errors.append("unmapped tasks: "+",".join(sorted(missing)))
 visiting,finished=set(),set()
 def walk(mid):
  if mid in visiting:errors.append("milestone cycle "+mid);return
  if mid in finished or mid not in byid:return
  visiting.add(mid)
  for dep in byid[mid]["depends_on"]:walk(dep)
  visiting.remove(mid);finished.add(mid)
 for mid in mids:walk(mid)
 return sorted(set(errors))
def main():
 schema=load("schemas/project-goals.v1.json")
 data=load("orchestration/planner/goals.json")
 queue=load("orchestration/planner/queue.json")
 Draft202012Validator.check_schema(schema)
 errors=[str(e.message) for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(data)]
 if not errors:errors=validate(data,queue)
 print(json.dumps({"status":"PASS" if not errors else "FAIL","goal_count":len(data["goals"]),"milestone_count":len(data["milestones"]),"task_count":len(queue["tasks"]),"errors":errors},indent=2))
 return 1 if errors else 0
if __name__=="__main__":sys.exit(main())
