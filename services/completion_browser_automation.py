"""Setup 5.02: browser automation foundation.
Defines bounded browser sessions, targets, actions, results and safety policy.
This layer is transport-neutral and never claims an action occurred without evidence.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
VERSION=1; MAX_ACTIONS=64

def _digest(p): return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]

@dataclass
class BrowserTarget:
    url:str=''; tab_id:str=''; title:str=''
    def to_dict(self): return asdict(self)

@dataclass
class BrowserAction:
    action:str; selector:str=''; value:str=''; timeout_ms:int=5000
    def to_dict(self): return asdict(self)

@dataclass
class BrowserResult:
    success:bool; action:dict; evidence:dict; error:str=''
    def to_dict(self): return asdict(self)

@dataclass
class BrowserSafetyPolicy:
    allowed_hosts:list[str]
    allow_external_hosts:bool=False
    max_actions:int=64
    def allows(self,url):
        from urllib.parse import urlparse
        host=(urlparse(url).hostname or '').lower()
        return bool(self.allow_external_hosts or host in {h.lower() for h in self.allowed_hosts})
    def to_dict(self): return asdict(self)

@dataclass
class BrowserSession:
    session_id:str; target:BrowserTarget; actions:list[dict]; policy:BrowserSafetyPolicy; status:str='ready'; digest:str=''
    def seal(self):
        payload={'session_id':self.session_id,'target':self.target.to_dict(),'actions':self.actions[:MAX_ACTIONS],'policy':self.policy.to_dict(),'status':self.status}
        self.digest=_digest(payload); return self
    def to_dict(self):
        self.seal(); d=asdict(self); d['browser_automation_version']=VERSION; return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get('browser_automation_version')!=VERSION:return None
        try:
            t=BrowserTarget(**{k:str(d.get('target',{}).get(k,'')) for k in ('url','tab_id','title')})
            p=BrowserSafetyPolicy([str(x) for x in d.get('policy',{}).get('allowed_hosts',[])],bool(d.get('policy',{}).get('allow_external_hosts',False)),int(d.get('policy',{}).get('max_actions',MAX_ACTIONS)))
            return cls(str(d.get('session_id','')),t,[dict(x) for x in d.get('actions',[])][:MAX_ACTIONS],p,str(d.get('status','ready')),str(d.get('digest','')))
        except Exception:return None
    def valid(self):
        expected=_digest({'session_id':self.session_id,'target':self.target.to_dict(),'actions':self.actions[:MAX_ACTIONS],'policy':self.policy.to_dict(),'status':self.status})
        return expected==self.digest

def create_session(session_id,url,allowed_hosts=None):
    policy=BrowserSafetyPolicy(list(allowed_hosts or ['localhost','127.0.0.1']))
    return BrowserSession(str(session_id),BrowserTarget(str(url)),[],policy).seal()
