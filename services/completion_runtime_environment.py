"""Setup 4.94: runtime dependency and environment mapping."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
from pathlib import Path
import json,re
VERSION=1; MAX_DEPS=160; MAX_ENV=160
def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
def _env(root,paths):
 keys=[]
 for r in paths:
  try:t=(root/r).read_text(encoding='utf-8',errors='ignore')
  except OSError:continue
  for line in t.splitlines():
   m=re.match(r'\s*([A-Za-z_][A-Za-z0-9_]*)\s*=',line)
   if m:keys.append(m.group(1))
 return list(dict.fromkeys(keys))[:MAX_ENV]
def _deps(root,manifests):
 out=[]
 for r in manifests:
  p=root/r
  try:t=p.read_text(encoding='utf-8',errors='ignore')
  except OSError:continue
  if p.name=='package.json':
   try:
    d=json.loads(t)
    for sec in ('dependencies','devDependencies','peerDependencies'):
     out += [str(x) for x in (d.get(sec) or {}).keys()]
   except Exception:pass
  elif p.name=='requirements.txt':
   for line in t.splitlines():
    line=line.strip()
    if line and not line.startswith('#'):out.append(re.split(r'[<=>~!;\[]',line,1)[0].strip())
  elif p.name=='pyproject.toml':
   out += re.findall(r'^\s*([A-Za-z0-9_.-]+)\s*(?:[<=>~!]|\[)',t,re.M)
 return list(dict.fromkeys(x for x in out if x))[:MAX_DEPS]
def build_environment_map(root_dir,profile):
 root=Path(root_dir).resolve(); env_keys=_env(root,profile.env_files); deps=_deps(root,profile.manifests)
 services=[]
 for p in profile.ports: services.append({'port':p,'source':'runtime profile'})
 payload={'root':root.as_posix(),'dependency_names':deps,'environment_keys':env_keys,'services':services}; return RuntimeEnvironment(root.as_posix(),deps,env_keys,services,_digest(payload))
@dataclass
class RuntimeEnvironment:
 root:str; dependency_names:list[str]; environment_keys:list[str]; services:list[dict]; digest:str
 def to_dict(self):d=asdict(self);d['runtime_environment_version']=VERSION;return d
 @classmethod
 def from_dict(cls,d):
  if not isinstance(d,dict) or d.get('runtime_environment_version')!=VERSION:return None
  return cls(str(d.get('root','')),[str(x) for x in d.get('dependency_names',[])][:MAX_DEPS],[str(x) for x in d.get('environment_keys',[])][:MAX_ENV],[dict(x) for x in d.get('services',[])][:32],str(d.get('digest','')))
 def valid(self):return _digest({'root':self.root,'dependency_names':self.dependency_names,'environment_keys':self.environment_keys,'services':self.services})==self.digest
