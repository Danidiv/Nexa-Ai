"""Setup 5.00: deterministic browser interaction/user-flow planning.
Planning only; no clicks or script execution.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
VERSION=1; MAX_STEPS=32

def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class BrowserAction:
    action:str; selector:str=''; value:str=''; expected:str=''
    def to_dict(self):return asdict(self)
@dataclass
class BrowserFlow:
    url:str; actions:list[dict]; digest:str
    def to_dict(self):d=asdict(self);d['browser_flow_version']=VERSION;return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get('browser_flow_version')!=VERSION:return None
        try:return cls(str(d.get('url','')),[dict(x) for x in d.get('actions',[])][:MAX_STEPS],str(d.get('digest','')))
        except Exception:return None
    def valid(self):return _digest({'url':self.url,'actions':self.actions})==self.digest
def build_user_flow(url, inspection, intent='verify page'):
    acts=[]
    if inspection.forms: acts.append(BrowserAction('inspect_form', 'form', '', 'form is present').to_dict())
    if inspection.buttons: acts.append(BrowserAction('inspect_controls', 'button,input[type=submit],input[type=button]', '', 'controls are present').to_dict())
    acts.append(BrowserAction('assert_page', 'body', '', intent).to_dict())
    acts=acts[:MAX_STEPS]; payload={'url':str(url),'actions':acts}; return BrowserFlow(payload['url'],acts,_digest(payload))
