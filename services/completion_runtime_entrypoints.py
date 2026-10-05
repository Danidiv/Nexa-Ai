"""Setup 4.93: application entry-point discovery."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
from pathlib import Path
VERSION=1; MAX_ENTRIES=64
NAMES={'main.py':'python','app.py':'python','manage.py':'python','server.py':'python','index.js':'node','index.ts':'node','main.js':'node','main.ts':'node','server.js':'node','server.ts':'node','vite.config.js':'node','vite.config.ts':'node','next.config.js':'node','next.config.mjs':'node','src/main.tsx':'frontend','src/main.jsx':'frontend','src/main.ts':'frontend','src/main.js':'frontend','src/App.tsx':'frontend','src/App.jsx':'frontend'}
def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
def discover_entrypoints(root_dir,profile=None):
 root=Path(root_dir).resolve(); entries=[]
 for name,kind in NAMES.items():
  p=root/name
  if p.is_file(): entries.append({'path':name,'kind':kind,'reason':'conventional entry point'})
 # package scripts are entrypoint commands
 if profile:
  for key,val in sorted(profile.scripts.items()):
   if key.lower() in {'dev','start','serve'}: entries.append({'path':f'package.json#scripts.{key}','kind':'command','reason':val})
 # Python console/ASGI/Flask hints
 for p in root.rglob('*.py'):
  if any(x in p.parts for x in ('.venv','venv','__pycache__','node_modules')): continue
  try:t=p.read_text(encoding='utf-8',errors='ignore')
  except OSError:continue
  if 'FastAPI(' in t or 'Flask(' in t or 'uvicorn.run' in t:
   rel=p.relative_to(root).as_posix(); entries.append({'path':rel,'kind':'python-server','reason':'framework/runtime entry signal'})
 entries=entries[:MAX_ENTRIES]; payload={'root':root.as_posix(),'entries':entries}; return EntryPointIndex(payload['root'],entries,_digest(payload))
@dataclass
class EntryPointIndex:
 root:str; entries:list[dict]; digest:str
 def to_dict(self):d=asdict(self);d['entrypoint_index_version']=VERSION;return d
 @classmethod
 def from_dict(cls,d):
  if not isinstance(d,dict) or d.get('entrypoint_index_version')!=VERSION:return None
  return cls(str(d.get('root','')),[dict(x) for x in d.get('entries',[])][:MAX_ENTRIES],str(d.get('digest','')))
 def valid(self):return _digest({'root':self.root,'entries':self.entries})==self.digest
