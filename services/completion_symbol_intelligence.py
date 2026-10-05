"""Setup 4.87: symbol-aware code intelligence.

Builds deterministic symbol records from the existing 4.82 codebase index.
No execution and no model calls.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import ast, json, re
from pathlib import Path

VERSION=1; MAX_SYMBOLS=240

@dataclass(frozen=True)
class SymbolRecord:
    path:str; name:str; kind:str; line:int; end_line:int
    def to_dict(self): return asdict(self)

@dataclass
class SymbolIndex:
    symbols:list[dict]
    digest:str
    def to_dict(self):
        d=asdict(self); d["symbol_index_version"]=VERSION; return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get("symbol_index_version")!=VERSION:return None
        try:return cls([dict(x) for x in d.get("symbols",[])][:MAX_SYMBOLS],str(d.get("digest","")))
        except Exception:return None

def _py_symbols(path,content):
    out=[]
    try: tree=ast.parse(content)
    except SyntaxError:return out
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            out.append(SymbolRecord(path,n.name,"function",n.lineno,getattr(n,"end_lineno",n.lineno)))
        elif isinstance(n,ast.ClassDef):
            out.append(SymbolRecord(path,n.name,"class",n.lineno,getattr(n,"end_lineno",n.lineno)))
    return out

def _text_symbols(path,content):
    out=[]
    patterns=[("function",r"\b(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)"),
              ("class",r"\bclass\s+([A-Za-z_$][\w$]*)"),
              ("variable",r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*="),
              ("interface",r"\binterface\s+([A-Za-z_$][\w$]*)"),
              ("type",r"\btype\s+([A-Za-z_$][\w$]*)")]
    for kind,pat in patterns:
        for m in re.finditer(pat,content):
            line=content.count("\n",0,m.start())+1
            out.append(SymbolRecord(path,m.group(1),kind,line,line))
    return out

def build_symbol_index(codebase_index):
    records=[]
    root=Path(codebase_index.root)
    for row in codebase_index.files:
        path=str(row.get("path","")); p=root/path
        try: content=p.read_text(encoding="utf-8",errors="ignore")
        except OSError: content=""
        if p.suffix.lower()==".py": records.extend(_py_symbols(path,content))
        else: records.extend(_text_symbols(path,content))
    records=sorted(records,key=lambda s:(s.path,s.line,s.name,s.kind))[:MAX_SYMBOLS]
    rows=[x.to_dict() for x in records]
    digest=sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
    return SymbolIndex(rows,digest)
