"""Setup 4.97: deterministic browser intelligence foundation.
No browser launch; discovers preview URLs, routes and browser-relevant artifacts.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
import json, re
VERSION=1; MAX_ROUTES=128

def _digest(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]

def discover_browser_surface(root_dir, runtime_profile=None, entrypoints=None):
    root=Path(root_dir).resolve(); routes=[]; urls=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file() or any(x in p.parts for x in {'.git','node_modules','dist','build','__pycache__','.venv','venv'}): continue
        try: t=p.read_text(encoding='utf-8',errors='ignore')
        except OSError: continue
        rel=p.relative_to(root).as_posix()
        for m in re.finditer(r'https?://(?:localhost|127\.0\.0\.1)(?::\d+)?(?:/[^\s"\'<>)]*)?',t): urls.append(m.group(0).rstrip('.,;'))
        if p.suffix.lower() in {'.html','.htm'}: routes.append({'path':rel,'route':'/','kind':'html'})
        if p.suffix.lower() in {'.tsx','.jsx','.ts','.js'} and re.search(r'(?i)(react-router|createBrowserRouter|<Route\b|router\.)',t): routes.append({'path':rel,'route':'dynamic','kind':'router-source'})
    ports=[] if runtime_profile is None else list(getattr(runtime_profile,'ports',[]) or [])
    if not urls and ports: urls=[f'http://localhost:{ports[0]}']
    urls=list(dict.fromkeys(urls))[:MAX_ROUTES]; routes=routes[:MAX_ROUTES]
    payload={'root':root.as_posix(),'urls':urls,'routes':routes}
    return BrowserSurface(root.as_posix(),urls,routes,_digest(payload))
@dataclass
class BrowserSurface:
    root:str; urls:list[str]; routes:list[dict]; digest:str
    def to_dict(self): d=asdict(self); d['browser_surface_version']=VERSION; return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get('browser_surface_version')!=VERSION:return None
        try:return cls(str(d.get('root','')),[str(x) for x in d.get('urls',[])][:MAX_ROUTES],[dict(x) for x in d.get('routes',[])][:MAX_ROUTES],str(d.get('digest','')))
        except Exception:return None
    def valid(self): return _digest({'root':self.root,'urls':self.urls,'routes':self.routes})==self.digest
