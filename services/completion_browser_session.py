"""Setup 5.81: persistent browser session contract."""
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class BrowserSessionSnapshot:
    session_id:str; browser:str='chromium'; active_target:str=''; tabs:list=None; state:str='active'; digest:str=''
    def __post_init__(self): self.tabs=list(self.tabs or [])
    def seal(self): self.digest=_d({'session_id':self.session_id,'browser':self.browser,'active_target':self.active_target,'tabs':self.tabs,'state':self.state}); return self
    def to_dict(self): d=asdict(self); d['browser_session_version']=VERSION; return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get('browser_session_version')!=VERSION:return None
        return cls(str(d.get('session_id','')),str(d.get('browser','chromium')),str(d.get('active_target','')),[str(x) for x in d.get('tabs',[])],str(d.get('state','active')),str(d.get('digest','')))
    def valid(self): return _d({'session_id':self.session_id,'browser':self.browser,'active_target':self.active_target,'tabs':self.tabs,'state':self.state})==self.digest
def create_session(session_id,browser='chromium'):
    return BrowserSessionSnapshot(session_id,browser).seal()
def restore_session(snapshot):
    s=BrowserSessionSnapshot.from_dict(snapshot); return s if s and s.valid() else None
