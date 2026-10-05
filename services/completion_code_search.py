"""Setup 4.83: deterministic bounded semantic-ish code search.

Uses normalized lexical tokens over the 4.82 index; no model calls and no code execution.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
import re
from typing import Any
from services.completion_codebase_index import CodebaseIndex
VERSION=1; MAX_RESULTS=12; MAX_QUERY=160

@dataclass
class CodeSearchResult:
    path:str; score:int; matches:list[str]
    def to_dict(self):return asdict(self)

def _tokens(text):return set(re.findall(r"[A-Za-z_][A-Za-z0-9_.$/-]*",str(text).lower()))

def search_code(index:CodebaseIndex,query:str,limit:int=MAX_RESULTS)->list[CodeSearchResult]:
    q=_tokens(str(query)[:MAX_QUERY]); out=[]
    for row in index.files:
        path=str(row.get("path","")); ext=str(row.get("extension","")); syms=index.symbols.get(path,[]); imps=index.imports.get(path,[])
        fields=[path.lower(),ext.lower()]+[str(x).lower() for x in syms]+[str(x).lower() for x in imps]
        score=sum(2 for t in q if any(t in f for f in fields))
        exact=sum(1 for t in q if any(t==f for f in fields))
        score+=exact
        if score:out.append(CodeSearchResult(path,score,[t for t in sorted(q) if any(t in f for f in fields)][:8]))
    return sorted(out,key=lambda r:(-r.score,r.path))[:max(1,min(int(limit),MAX_RESULTS))]

def search_to_dict(index,query,limit=MAX_RESULTS):
    return {"version":VERSION,"query":str(query)[:MAX_QUERY],"results":[r.to_dict() for r in search_code(index,query,limit)]}
