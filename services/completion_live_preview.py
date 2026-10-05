"""Setup 4.98: safe live-preview runtime contract.
Tracks a preview command and lifecycle metadata; execution is opt-in via start().
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json, subprocess, time, os
VERSION=1; MAX_CMD=240

def _digest(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class PreviewState:
    status:str='not_started'; command:list[str]=None; url:str=''; pid:int=0; started_at:float=0.0; digest:str=''
    def __post_init__(self): self.command=list(self.command or [])
    def to_dict(self): d=asdict(self); d['live_preview_version']=VERSION; return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get('live_preview_version')!=VERSION:return None
        try:return cls(str(d.get('status','not_started')),[str(x) for x in d.get('command',[])][:16],str(d.get('url','')),int(d.get('pid',0)),float(d.get('started_at',0)),str(d.get('digest','')))
        except Exception:return None
    def valid(self): return _digest({'status':self.status,'command':self.command,'url':self.url,'pid':self.pid,'started_at':self.started_at})==self.digest
class LivePreview:
    def __init__(self, command=None, url=''):
        self.state=PreviewState(command=list(command or []),url=url); self._process=None; self._seal()
    def _seal(self):
        self.state.digest=_digest({'status':self.state.status,'command':self.state.command,'url':self.state.url,'pid':self.state.pid,'started_at':self.state.started_at})
    def start(self, cwd=None):
        if self.state.status=='running': return False
        if not self.state.command: return False
        self._process=subprocess.Popen(self.state.command,cwd=cwd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0))
        self.state.status='running'; self.state.pid=self._process.pid; self.state.started_at=time.time(); self._seal(); return True
    def stop(self):
        if self._process is not None and self._process.poll() is None: self._process.terminate()
        self.state.status='stopped'; self.state.pid=0; self._seal(); return True
    def healthy(self): return self.state.status=='running' and self._process is not None and self._process.poll() is None
