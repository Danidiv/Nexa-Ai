"""Setup 4.85: deterministic multi-file change planning from search + graph."""
from __future__ import annotations
from dataclasses import dataclass,asdict
VERSION=1;MAX_PATHS=16
@dataclass
class CodeChangePlan:
    query:str; targets:list[str]; inspect:list[str]; change:list[str]; verify:list[str]; rationale:list[str]
    def to_dict(self):d=asdict(self);d["code_change_plan_version"]=VERSION;return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get("code_change_plan_version")!=VERSION:return None
        try:return cls(str(d.get("query","")),*[ [str(x) for x in d.get(k,[])][:MAX_PATHS] for k in ("targets","inspect","change","verify") ],[str(x) for x in d.get("rationale",[])][:8])
        except Exception:return None

def build_code_change_plan(query,search_results,graph):
    targets=[]
    for r in search_results[:MAX_PATHS]:
        p=str(r.get("path",""));
        if p and p not in targets:targets.append(p)
    deps=[];dependents=[]
    for p in targets:
        deps.extend(graph.edges.get(p,[]));dependents.extend(graph.reverse.get(p,[]))
    deps=list(dict.fromkeys(x for x in deps if x not in targets))[:MAX_PATHS]
    dependents=list(dict.fromkeys(x for x in dependents if x not in targets and x not in deps))[:MAX_PATHS]
    inspect=list(dict.fromkeys(deps+targets+dependents))[:MAX_PATHS]
    verify=list(dict.fromkeys(targets+dependents))[:MAX_PATHS]
    rationale=["Search hits are candidate targets, not proof of required edits.","Dependencies are inspected before target changes.","Dependents are included for post-change verification.","Actual file reads and tool results remain authoritative."]
    return CodeChangePlan(str(query)[:160],targets,inspect,targets[:MAX_PATHS],verify,rationale)
