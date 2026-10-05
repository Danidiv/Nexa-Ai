"""Setup 4.82: bounded codebase intelligence index.

Builds deterministic metadata about source files, symbols, imports, and content
hashes without executing project code.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from hashlib import sha256
import ast, os, re
from typing import Any

VERSION=1
MAX_FILES=120
MAX_BYTES=48_000
MAX_SYMBOLS=40
SUPPORTED={".py",".js",".jsx",".ts",".tsx",".mjs",".cjs",".vue",".svelte",".html",".css"}
SKIP={".git","node_modules","__pycache__",".venv","venv","dist","build"}

@dataclass
class CodebaseIndex:
    files: list[dict[str,Any]]
    symbols: dict[str,list[str]]
    imports: dict[str,list[str]]
    root: str
    digest: str
    def to_dict(self):
        d=asdict(self); d["codebase_index_version"]=VERSION; return d
    @classmethod
    def from_dict(cls,data):
        if not isinstance(data,dict) or data.get("codebase_index_version")!=VERSION:return None
        try:
            return cls(list(data.get("files") or [])[:MAX_FILES],{str(k):[str(x) for x in v][:MAX_SYMBOLS] for k,v in (data.get("symbols") or {}).items()}, {str(k):[str(x) for x in v][:MAX_SYMBOLS] for k,v in (data.get("imports") or {}).items()},str(data.get("root","")),str(data.get("digest","")))
        except Exception:return None

def _files(root:Path):
    out=[]
    if not root.is_dir():return out
    for cur,dirs,names in os.walk(root):
        dirs[:]=[d for d in sorted(dirs) if d not in SKIP][:40]
        for n in sorted(names):
            p=Path(cur)/n
            if p.suffix.lower() in SUPPORTED:
                out.append(p)
                if len(out)>=MAX_FILES:return out
    return out

def _rel(p,root):
    try:return p.resolve().relative_to(root.resolve()).as_posix()
    except Exception:return p.name

def _read(p):
    try:
        if p.stat().st_size>MAX_BYTES:return ""
        return p.read_text(encoding="utf-8",errors="ignore")
    except OSError:return ""

def _symbols(content,suffix):
    out=[]
    if suffix==".py":
        try:
            tree=ast.parse(content)
            for n in ast.walk(tree):
                if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                    out.append(n.name)
                elif isinstance(n,(ast.Assign,ast.AnnAssign)):
                    targets=n.targets if isinstance(n,ast.Assign) else [n.target]
                    for t in targets:
                        if isinstance(t,ast.Name):out.append(t.id)
        except SyntaxError:pass
    else:
        pats=[r"\b(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)",r"\bclass\s+([A-Za-z_$][\w$]*)",r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=",r"\binterface\s+([A-Za-z_$][\w$]*)",r"\btype\s+([A-Za-z_$][\w$]*)"]
        for pat in pats:
            out.extend(re.findall(pat,content))
    return list(dict.fromkeys(out))[:MAX_SYMBOLS]

def _imports(content,suffix):
    pats=[]
    if suffix==".py":pats=[r"^\s*from\s+([.\w]+)\s+import\s+",r"^\s*import\s+([.\w]+)"]
    elif suffix in {".js",".jsx",".ts",".tsx",".mjs",".cjs",".vue",".svelte"}:pats=[r"(?:from\s+|require\s*\(|import\s*(?:\(|\s+))\s*[\"']([^\"']+)"]
    else:pats=[r"(?:src|href)\s*=\s*[\"']([^\"'#]+)"]
    out=[]
    for pat in pats:out.extend(m.group(1) for m in re.finditer(pat,content,re.I|re.M))
    return list(dict.fromkeys(x for x in out if not x.startswith(("http:","https:","data:","#"))))[:MAX_SYMBOLS]

def _digest(files,symbols,imports,root):
    payload={"files":files,"symbols":symbols,"imports":imports,"root":root}
    return sha256(__import__("json").dumps(payload,sort_keys=True,separators=(",",":" )).encode()).hexdigest()[:24]

def build_codebase_index(root_dir:str)->CodebaseIndex:
    root=Path(root_dir).resolve(); rows=[]; symbols={}; imports={}
    for p in _files(root):
        rel=_rel(p,root); content=_read(p)
        try:size=p.stat().st_size
        except OSError:size=0
        rows.append({"path":rel,"extension":p.suffix.lower(),"size":int(size),"content_hash":sha256(content.encode()).hexdigest()[:24]})
        symbols[rel]=_symbols(content,p.suffix.lower())
        imports[rel]=_imports(content,p.suffix.lower())
    digest=_digest(rows,symbols,imports,root.as_posix())
    return CodebaseIndex(rows,symbols,imports,root.as_posix(),digest)
