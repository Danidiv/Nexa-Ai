"""Setup 5.10: integrated browser development loop.
Combines codebase/runtime/browser intelligence into one deterministic verification contract.
"""
from __future__ import annotations
from hashlib import sha256
import json
from services.completion_browser_runtime_integration import browser_runtime_report,validate_browser_runtime_report
from services.completion_browser_automation import BrowserSession,create_session
from services.completion_browser_navigation import navigation_plan
from services.completion_browser_dom import discover
from services.completion_browser_actions import execute_flow
from services.completion_browser_diagnostics import collect,summarize
from services.completion_browser_debugging import build_repair_plan
VERSION=1

def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]

def development_loop_contract(root_dir,html,url,actions=None,events=None,query='application'):
    integrated=browser_runtime_report(root_dir,html,url,query)
    session=create_session('dev-loop',url,['localhost','127.0.0.1'])
    dom=discover(html,url)
    diagnostics=collect(events)
    repair=build_repair_plan(diagnostics,integrated.get('codebase'),integrated.get('runtime'))
    payload={'integrated':integrated,'session':session.to_dict(),'navigation':navigation_plan(url),'dom':dom.to_dict(),'actions':[dict(x) for x in (actions or [])],'diagnostics':diagnostics.to_dict(),'repair':repair.to_dict()}
    return {'version':VERSION,'status':'repair_required' if repair.issue_type!='none' else 'ready','integrated':integrated,'session':session.to_dict(),'navigation':navigation_plan(url),'dom':dom.to_dict(),'actions':[dict(x) for x in (actions or [])],'diagnostics':diagnostics.to_dict(),'diagnostic_summary':summarize(diagnostics),'repair':repair.to_dict(),'digest':_digest(payload)}

def validate_development_loop(report):
    if not isinstance(report,dict) or report.get('version')!=VERSION:return False
    if not validate_browser_runtime_report(report.get('integrated')):return False
    session=BrowserSession.from_dict(report.get('session')); dom=discover(report['dom'].get('html',''),report.get('session',{}).get('target',{}).get('url','')) if False else None
    if not session or not session.valid():return False
    if report.get('diagnostics',{}).get('browser_diagnostics_version')!=1:return False
    # validate immutable digest over the returned contract
    payload={k:report[k] for k in ('integrated','session','navigation','dom','actions','diagnostics','repair')}
    return _digest(payload)==report.get('digest')
