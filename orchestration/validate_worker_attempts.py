#!/usr/bin/env python3
"""Worker attempt ledger QC. Lessons are proposed procedural revisions, not model weight training."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(Path(path).read_text(encoding="utf-8"))
def evaluate(ledger,scopes):
 errors=[]
 selected=[s for s in scopes["scopes"] if s["task_id"]==ledger["task_id"] and s["spark_id"]==ledger["spark_id"]]
 if len(selected)!=1:return ["unknown or duplicate task/spark scope"]
 valid_steps={s["step_id"] for s in selected[0]["steps"]}
 seen=set()
 counts={"passed":0,"failed":0,"blocked":0,"unverified":0}
 byid={}
 for a in ledger["attempts"]:
  if a["attempt_id"] in seen:errors.append("duplicate attempt ID "+a["attempt_id"])
  seen.add(a["attempt_id"]);byid[a["attempt_id"]]=a
  if a["step_id"] not in valid_steps:errors.append("outside task recipe "+a["step_id"])
  counts[a["state"]]+=1
  if a["state"]=="passed" and not a["evidence"]:errors.append("unproven pass "+a["attempt_id"])
  if a["state"]=="failed" and not a["resolution"]:errors.append("unresolved failure "+a["attempt_id"])
  if a["retry_of"] and (a["retry_of"] not in byid or byid[a["retry_of"]]["step_id"]!=a["step_id"]):
   errors.append("invalid retry lineage "+a["attempt_id"])
  if a["time_spent_seconds"] is None and ledger["evaluation"]["measured_time_seconds"] is not None:
   errors.append("aggregate time cannot claim completeness when attempt time missing")
  if a["tool_calls"] is None and ledger["evaluation"]["measured_tool_calls"] is not None:
   errors.append("aggregate tools cannot claim completeness when attempt calls missing")
 ev=ledger["evaluation"]
 for k,v in counts.items():
  if ev[k]!=v:errors.append("incorrect count for "+k)
 if ev["total_attempts"]!=len(ledger["attempts"]):errors.append("attempt count mismatch")
 if all(a["time_spent_seconds"] is not None for a in ledger["attempts"]):
  if ev["measured_time_seconds"]!=sum(a["time_spent_seconds"] for a in ledger["attempts"]):errors.append("measured time sum mismatch")
 if all(a["tool_calls"] is not None for a in ledger["attempts"]):
  if ev["measured_tool_calls"]!=sum(a["tool_calls"] for a in ledger["attempts"]):errors.append("tool count mismatch")
 first=[a for a in ledger["attempts"] if a["retry_of"] is None]
 expected=sum(a["state"]=="passed" for a in first)/len(first) if first else None
 if ev["first_pass_rate"]!=expected:errors.append("first-pass rate mismatch")
 lessons=set()
 for l in ledger["lessons"]:
  if l["lesson_id"] in lessons:errors.append("duplicate lesson")
  lessons.add(l["lesson_id"])
  if l["from_attempt"] not in byid:errors.append("untraceable lesson "+l["lesson_id"])
  elif byid[l["from_attempt"]]["state"]!="failed":errors.append("lesson must originate from failed attempt")
  if l["status"]=="adopted" and not any(a["state"]=="passed" and a["retry_of"]==l["from_attempt"] for a in ledger["attempts"]):
   errors.append("lesson adopted without successful corrective retry "+l["lesson_id"])
 return errors
def main():
 ledger=read(sys.argv[1] if len(sys.argv)>1 else ROOT/"orchestration/planner/attempts/T-001.json")
 scopes=read(ROOT/"orchestration/planner/worker-scopes.json")
 errors=evaluate(ledger,scopes)
 print(json.dumps({"status":"pass" if not errors else "fail","errors":errors,"attempts":len(ledger["attempts"]),"note":"procedure/fixture validation only, not an autonomous-trained model"},indent=2))
 return bool(errors)
if __name__=="__main__":raise SystemExit(main())
