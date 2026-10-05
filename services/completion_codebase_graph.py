"""Setup 4.84: normalized dependency graph derived from the codebase index."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Any
VERSION=1; MAX_NODES=120; MAX_EDGES=300; MAX_NEIGHBORS=16
@dataclass
class CodebaseGraph:
    nodes:list[str]; edges:dict[str,list[str]]; reverse:dict[str,list[str]]; cycles:list[list[str]]; digest:str
    def to_dict(self):d=asdict(self);d["codebase_graph_version"]=VERSION;return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get("codebase_graph_version")!=VERSION:return None
        try:return cls([str(x) for x in d.get("nodes",[])][:MAX_NODES],{str(k):[str(x) for x in v][:MAX_NEIGHBORS] for k,v in (d.get("edges") or {}).items()},{str(k):[str(x) for x in v][:MAX_NEIGHBORS] for k,v in (d.get("reverse") or {}).items()},[[str(x) for x in c][:MAX_NODES] for c in d.get("cycles",[])][:8],str(d.get("digest","")))
        except Exception:return None

def _resolve(src,raw,nodes):
    r=str(raw).split("?",1)[0].split("#",1)[0].replace("\\","/")
    if not r.startswith("."):return None
    base=(__import__("pathlib").PurePosixPath(src).parent/__import__("pathlib").PurePosixPath(r)).as_posix().lstrip("./")
    candidates=[base]+[base+e for e in (".js",".jsx",".ts",".tsx",".py",".vue",".svelte",".html",".css")]+[base+"/index.js",base+"/index.ts",base+"/__init__.py"]
    return next((c for c in candidates if c in nodes),None)

def build_graph(index):
    import hashlib,json
    nodes=sorted(str(x.get("path","")) for x in index.files)[:MAX_NODES]; edges={n:[] for n in nodes}; rev={n:[] for n in nodes}; count=0
    for src in nodes:
        for raw in index.imports.get(src,[])[:MAX_NEIGHBORS]:
            dst=_resolve(src,raw,nodes)
            if dst and dst!=src and dst not in edges[src] and count<MAX_EDGES:
                edges[src].append(dst);rev[dst].append(src);count+=1
    cycles=[]; visiting=set();stack=[]
    def dfs(n):
        if n in stack:
            cycles.append(stack[stack.index(n):]+[n]);return
        if n in visiting:return
        visiting.add(n);stack.append(n)
        for d in edges.get(n,[]):dfs(d)
        stack.pop()
    for n in nodes:dfs(n)
    payload={"nodes":nodes,"edges":edges,"reverse":rev,"cycles":cycles[:8]};dig=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
    return CodebaseGraph(nodes,edges,rev,cycles[:8],dig)

def neighbors(graph,path):
    p=str(path).replace("\\","/").lstrip("./");return {"dependencies":graph.edges.get(p,[])[:MAX_NEIGHBORS],"dependents":graph.reverse.get(p,[])[:MAX_NEIGHBORS]}
