"""Setup 4.92: deterministic runtime intelligence foundation.

Inspects project metadata without executing application code. It identifies runtime
family, package manifests, scripts, candidate ports, environment files, and common
run/build/test commands.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
import json, re
VERSION=1; MAX_FILES=80; MAX_COMMANDS=32
SKIP={".git","node_modules","__pycache__",".venv","venv","dist","build",".next","target"}
MANIFESTS={"package.json":"node","pyproject.toml":"python","requirements.txt":"python","Pipfile":"python","poetry.lock":"python","Cargo.toml":"rust","go.mod":"go","pom.xml":"java","build.gradle":"java"}

def _digest(payload): return sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]

def _walk(root):
 out=[]
 if not root.is_dir(): return out
 for cur,dirs,names in __import__('os').walk(root):
  dirs[:]=[d for d in sorted(dirs) if d not in SKIP][:32]
  for n in sorted(names):
   p=Path(cur)/n
   if p.is_file(): out.append(p)
   if len(out)>=MAX_FILES:return out
 return out

def _read(p):
 try:
  if p.stat().st_size>120000:return ""
  return p.read_text(encoding='utf-8',errors='ignore')
 except OSError:return ""

def build_runtime_profile(root_dir:str):
 root=Path(root_dir).resolve(); files=_walk(root); rel=lambda p:p.relative_to(root).as_posix()
 manifests=[]; families=[]; scripts={}; env_files=[]; ports=set(); commands=[]
 for p in files:
  r=rel(p); name=p.name
  if name in MANIFESTS:
   manifests.append(r); families.append(MANIFESTS[name])
   if name=='package.json':
    try:
     d=json.loads(_read(p)); scripts.update({str(k):str(v) for k,v in (d.get('scripts') or {}).items()})
    except Exception: pass
  if name.startswith('.env') or name in {'.env.example','.env.local.example'}: env_files.append(r)
  txt=_read(p)
  for m in re.finditer(r'(?i)(?:port\s*[:=]\s*|listen\s*\(\s*|localhost:)(\d{2,5})',txt):
   n=int(m.group(1));
   if 1<=n<=65535: ports.add(n)
 for key,val in scripts.items():
  if any(x in key.lower() for x in ('dev','start','serve','build','test','lint','check')): commands.append(f"npm run {key}")
 if any(x in manifests for x in ('requirements.txt','pyproject.toml','Pipfile')):
  commands += ['python -m pytest','python -m pip install -r requirements.txt'] if 'requirements.txt' in manifests else ['python -m pytest']
 if 'Cargo.toml' in manifests: commands += ['cargo test','cargo run','cargo build']
 if 'go.mod' in manifests: commands += ['go test ./...','go run .','go build ./...']
 families=list(dict.fromkeys(families)); family=families[0] if families else 'unknown'
 commands=list(dict.fromkeys(commands))[:MAX_COMMANDS]
 payload={'root':root.as_posix(),'runtime_family':family,'runtime_families':families,'manifests':manifests,'scripts':dict(sorted(scripts.items())),'env_files':env_files,'ports':sorted(ports),'commands':commands}
 return RuntimeProfile(**payload,digest=_digest(payload))

@dataclass
class RuntimeProfile:
 root:str; runtime_family:str; runtime_families:list[str]; manifests:list[str]; scripts:dict[str,str]; env_files:list[str]; ports:list[int]; commands:list[str]; digest:str
 def to_dict(self): d=asdict(self); d['runtime_profile_version']=VERSION; return d
 @classmethod
 def from_dict(cls,d):
  if not isinstance(d,dict) or d.get('runtime_profile_version')!=VERSION:return None
  try:return cls(str(d.get('root','')),str(d.get('runtime_family','unknown')),[str(x) for x in d.get('runtime_families',[])], [str(x) for x in d.get('manifests',[])][:MAX_FILES], {str(k):str(v) for k,v in (d.get('scripts') or {}).items()}, [str(x) for x in d.get('env_files',[])][:MAX_FILES], [int(x) for x in d.get('ports',[])][:32], [str(x) for x in d.get('commands',[])][:MAX_COMMANDS], str(d.get('digest','')))
  except Exception:return None
 def valid(self):
  p=asdict(self); p.pop('digest',None); return _digest(p)==self.digest
