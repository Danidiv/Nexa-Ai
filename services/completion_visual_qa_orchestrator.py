from hashlib import sha256
import json
from services.completion_visual_qa_agent import visual_qa_report,valid_visual_qa_report
from services.completion_release_gate import evaluate_release,valid_release
from services.completion_qa_repair_planner import build_repair_plan,valid_repair_plan
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def orchestrate(url,html,baseline_hash,current_hash,metrics,extra_checks=None):
    qa=visual_qa_report(url,html,baseline_hash,current_hash,metrics)
    reports=[{"source":"visual_qa","status":"pass" if qa["status"]=="ready" else "issues"}] + list(extra_checks or [])
    repair=build_repair_plan(reports)
    gate=evaluate_release(reports)
    payload={"qa":qa,"repair":repair,"gate":gate}; return {"version":VERSION,"status":"ready" if gate["status"]=="ready" else "blocked",**payload,"digest":_d(payload)}
def valid_orchestration(r):
    if not isinstance(r,dict) or r.get("version")!=VERSION:return False
    payload={"qa":r.get("qa"),"repair":r.get("repair"),"gate":r.get("gate")}
    return r.get("digest")==_d(payload) and valid_visual_qa_report(r["qa"]) and valid_repair_plan(r["repair"]) and valid_release(r["gate"])
