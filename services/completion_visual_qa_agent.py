from hashlib import sha256
import json
from services.completion_accessibility import inspect_accessibility
from services.completion_visual_diff import compare_visual
from services.completion_performance import performance_report
from services.completion_accessibility_repair import build_accessibility_repair,valid_accessibility_repair
from services.completion_browser_qa_coordinator import coordinate_qa,valid_qa
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
def visual_qa_report(url,html,baseline_hash,current_hash,metrics):
 a=inspect_accessibility(html); v=compare_visual(baseline_hash,current_hash); p=performance_report(metrics); r=build_accessibility_repair(a); q=coordinate_qa(url,a,v,p); payload={'accessibility':a,'visual':v,'performance':p,'repair':r,'qa':q}; return {'version':VERSION,'status':'ready' if valid_accessibility_repair(r,a) and valid_qa(q,a,v,p) else 'blocked',**payload,'digest':_d(payload)}
def valid_visual_qa_report(r):
 if not isinstance(r,dict) or r.get('version')!=VERSION:return False
 payload={k:r.get(k) for k in ('accessibility','visual','performance','repair','qa')}; return r.get('digest')==_d(payload) and valid_accessibility_repair(r['repair'],r['accessibility']) and valid_qa(r['qa'],r['accessibility'],r['visual'],r['performance'])
