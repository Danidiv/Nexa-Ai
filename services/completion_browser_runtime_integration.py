"""Setup 5.01: browser + runtime + codebase integration contract."""
from __future__ import annotations
from hashlib import sha256
import json
from services.completion_runtime_intelligence_integration import runtime_intelligence_report,validate_runtime_report
from services.completion_codebase_intelligence import intelligence_report,validate_report
from services.completion_browser_intelligence import discover_browser_surface,BrowserSurface
from services.completion_browser_inspection import inspect_html,PageInspection
from services.completion_browser_interaction import build_user_flow,BrowserFlow
VERSION=2
def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
def browser_runtime_report(root_dir, html=None, url='', query=''):
    runtime=runtime_intelligence_report(root_dir)
    codebase=intelligence_report(root_dir,query or 'application')
    surface=discover_browser_surface(root_dir)
    preview_url=url or (surface.urls[0] if surface.urls else '')
    inspection=inspect_html(html or '<html><head><title>Preview</title></head><body><button>OK</button></body></html>',preview_url)
    flow=build_user_flow(inspection.url,inspection)
    payload={'runtime':runtime,'codebase':codebase,'surface':surface.to_dict(),'inspection':inspection.to_dict(),'flow':flow.to_dict()}
    return {'version':VERSION,'status':'ready' if validate_runtime_report(runtime) and validate_report(codebase) and surface.valid() and inspection.valid() and flow.valid() else 'blocked','runtime':runtime,'codebase':codebase,'surface':surface.to_dict(),'inspection':inspection.to_dict(),'flow':flow.to_dict(),'digest':_digest(payload)}
def validate_browser_runtime_report(report):
    if not isinstance(report,dict) or report.get('version')!=VERSION:return False
    s=BrowserSurface.from_dict(report.get('surface')); i=PageInspection.from_dict(report.get('inspection')); f=BrowserFlow.from_dict(report.get('flow'))
    if not s or not i or not f or not validate_runtime_report(report.get('runtime')) or not validate_report(report.get('codebase')):return False
    if not all([s.valid(),i.valid(),f.valid()]):return False
    payload={'runtime':report['runtime'],'codebase':report['codebase'],'surface':s.to_dict(),'inspection':i.to_dict(),'flow':f.to_dict()}
    return _digest(payload)==report.get('digest')
