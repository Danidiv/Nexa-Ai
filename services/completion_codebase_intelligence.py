"""Setup 4.86: integrated, deterministic codebase-intelligence report."""
from __future__ import annotations
from hashlib import sha256
import json
from services.completion_codebase_index import build_codebase_index,CodebaseIndex
from services.completion_code_search import search_code
from services.completion_codebase_graph import build_graph,CodebaseGraph
from services.completion_code_change_plan import build_code_change_plan
VERSION=1
def intelligence_report(root,query):
    index=build_codebase_index(root); results=search_code(index,query); graph=build_graph(index); plan=build_code_change_plan(query,[r.to_dict() for r in results],graph)
    payload={"index_digest":index.digest,"graph_digest":graph.digest,"targets":plan.targets,"inspect":plan.inspect,"verify":plan.verify,"query":plan.query}
    digest=sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
    return {"version":VERSION,"status":"ready" if index.digest and graph.digest else "blocked","index":index.to_dict(),"search":[r.to_dict() for r in results],"graph":graph.to_dict(),"plan":plan.to_dict(),"digest":digest}
def validate_report(report):
    if not isinstance(report,dict) or report.get("version")!=VERSION or report.get("status") not in {"ready","blocked"}:return False
    if not isinstance(report.get("index"),dict) or not isinstance(report.get("graph"),dict) or not isinstance(report.get("plan"),dict):return False
    i=CodebaseIndex.from_dict(report["index"]);g=CodebaseGraph.from_dict(report["graph"])
    if i is None or g is None:return False
    p=report["plan"]; payload={"index_digest":i.digest,"graph_digest":g.digest,"targets":p.get("targets",[]),"inspect":p.get("inspect",[]),"verify":p.get("verify",[]),"query":p.get("query","")}
    expected=sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
    return expected==report.get("digest")
