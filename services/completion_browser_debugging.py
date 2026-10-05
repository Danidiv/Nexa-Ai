"""Setup 5.09: autonomous browser debugging bridge.
Turns browser diagnostics into evidence-bound repair candidates using codebase/runtime intelligence.
Planning only; it does not edit files.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json,re
from services.completion_browser_diagnostics import BrowserDiagnostics
VERSION=1

def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class BrowserRepairPlan:
    issue_type:str; message:str; candidates:list[str]; evidence:list[dict]; priority:str='normal'; digest:str=''
    def seal(self):self.digest=_digest({'issue_type':self.issue_type,'message':self.message,'candidates':self.candidates,'evidence':self.evidence,'priority':self.priority});return self
    def to_dict(self):d=asdict(self);d['browser_debugging_version']=VERSION;return d
    def valid(self):return self.digest==_digest({'issue_type':self.issue_type,'message':self.message,'candidates':self.candidates,'evidence':self.evidence,'priority':self.priority})

def build_repair_plan(diagnostics, codebase_report=None, runtime_report=None):
    issues=[]
    for x in diagnostics.console_errors:issues.append(('console_error',str(x.get('message','console error')),x))
    for x in diagnostics.failed_requests:issues.append(('network_failure',str(x.get('url','network failure')),x))
    for x in diagnostics.uncaught_exceptions:issues.append(('uncaught_exception',str(x.get('message','uncaught exception')),x))
    if not issues:return BrowserRepairPlan('none','No browser failures detected',[],[],'none').seal()
    typ,msg,ev=issues[0]; candidates=[]
    blob=' '.join(str(v) for v in ev.values())
    if codebase_report:
        for item in codebase_report.get('files',[])[:80]:
            if any(tok.lower() in json.dumps(item).lower() for tok in re.findall(r'[A-Za-z_][A-Za-z0-9_]{2,}',blob)[:12]):candidates.append(str(item.get('path','')))
    if not candidates and codebase_report:
        candidates=[str(x.get('path','')) for x in codebase_report.get('files',[])[:3] if x.get('path')]
    return BrowserRepairPlan(typ,msg,candidates,[ev],'high').seal()
