"""Setup 5.08: browser console and network diagnostics contract."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
VERSION=1; MAX_EVENTS=200

def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class BrowserDiagnostics:
    console_errors:list[dict]; failed_requests:list[dict]; uncaught_exceptions:list[dict]; digest:str=''
    def seal(self):self.console_errors=self.console_errors[:MAX_EVENTS];self.failed_requests=self.failed_requests[:MAX_EVENTS];self.uncaught_exceptions=self.uncaught_exceptions[:MAX_EVENTS];self.digest=_digest({'console_errors':self.console_errors,'failed_requests':self.failed_requests,'uncaught_exceptions':self.uncaught_exceptions});return self
    def to_dict(self):d=asdict(self);d['browser_diagnostics_version']=VERSION;return d
    def valid(self):return self.digest==_digest({'console_errors':self.console_errors[:MAX_EVENTS],'failed_requests':self.failed_requests[:MAX_EVENTS],'uncaught_exceptions':self.uncaught_exceptions[:MAX_EVENTS]})

def collect(events=None):
    c=[];f=[];u=[]
    for e in list(events or []):
        kind=str(e.get('kind',''))
        if kind=='console_error':c.append(dict(e))
        elif kind=='network_failure':f.append(dict(e))
        elif kind=='uncaught_exception':u.append(dict(e))
    return BrowserDiagnostics(c,f,u).seal()

def summarize(d):return {'healthy':not (d.console_errors or d.failed_requests or d.uncaught_exceptions),'console_errors':len(d.console_errors),'failed_requests':len(d.failed_requests),'uncaught_exceptions':len(d.uncaught_exceptions)}
