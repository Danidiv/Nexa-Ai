"""Setup 4.88: cross-file symbol reference analysis."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json,re
VERSION=1; MAX_REFS=400

@dataclass(frozen=True)
class ReferenceRecord:
    source:str; symbol:str; target:str; line:int; kind:str
    def to_dict(self):return asdict(self)

@dataclass
class ReferenceIndex:
    references:list[dict]; by_symbol:dict[str,list[str]]; digest:str
    def to_dict(self):d=asdict(self);d["reference_index_version"]=VERSION;return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get("reference_index_version")!=VERSION:return None
        try:return cls([dict(x) for x in d.get("references",[])][:MAX_REFS],{str(k):[str(x) for x in v] for k,v in (d.get("by_symbol") or {}).items()},str(d.get("digest","")))
        except Exception:return None

def build_reference_index(codebase_index,symbol_index):
    symbols={str(x.get("name")):[] for x in symbol_index.symbols}
    for x in symbol_index.symbols:symbols.setdefault(str(x.get("name")),[]).append(str(x.get("path")))
    refs=[]
    for row in codebase_index.files:
        src=str(row.get("path",""));
        try: content=__import__('pathlib').Path(codebase_index.root,src).read_text(encoding='utf-8',errors='ignore')
        except OSError: continue
        for name,targets in symbols.items():
            if not name or not targets: continue
            for m in re.finditer(r"\b"+re.escape(name)+r"\b",content):
                line=content.count("\n",0,m.start())+1
                for target in targets:
                    if target!=src:
                        refs.append(ReferenceRecord(src,name,target,line,"symbol_reference"))
                        if len(refs)>=MAX_REFS: break
                if len(refs)>=MAX_REFS: break
            if len(refs)>=MAX_REFS: break
        if len(refs)>=MAX_REFS: break
    refs=sorted({(r.source,r.symbol,r.target,r.line,r.kind):r for r in refs}.values(),key=lambda r:(r.source,r.line,r.symbol,r.target))[:MAX_REFS]
    by={}
    for r in refs:by.setdefault(r.symbol,[]).append(r.source)
    by={k:sorted(set(v)) for k,v in sorted(by.items())}
    payload={"references":[r.to_dict() for r in refs],"by_symbol":by}
    dig=sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
    return ReferenceIndex(payload["references"],by,dig)

def references_for_path(index,path):
    p=str(path).replace('\\','/')
    return [r for r in index.references if r.get('source')==p or r.get('target')==p]
