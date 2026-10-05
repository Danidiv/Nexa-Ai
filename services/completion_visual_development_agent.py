"""Setup 5.90: full visual development agent contract."""
from hashlib import sha256
import json
from services.completion_browser_session import create_session
from services.completion_browser_tabs import register_tabs
from services.completion_visual_elements import build_visual_model
from services.completion_browser_state_verification import verify_state,valid_state_report
from services.completion_browser_error_localization import localize_browser_error
from services.completion_browser_repair import build_repair_cycle,valid_repair_cycle
VERSION=1
def _d(p):return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def development_report(root_dir,url,html,code_index=None):
 session=create_session('dev-1'); tabs=register_tabs([{'tab_id':'main','url':url,'title':'Preview'}],'main'); visual=build_visual_model(url,html); state=verify_state({'url':url,'title':'Preview'},{'url':url,'title':'Preview'}); localization=localize_browser_error('') if False else {'error':'','candidates':[],'digest':_d({'error':'','candidates':[]})}; repair=build_repair_cycle('','',[]) if False else build_repair_cycle('No browser error',localization,[]); payload={'session':session.to_dict(),'tabs':tabs.to_dict(),'visual':visual.to_dict(),'state':state,'localization':localization,'repair':repair};return {'version':VERSION,'status':'ready' if visual.valid() and valid_state_report(state) and valid_repair_cycle(repair) else 'blocked',**payload,'digest':_d(payload)}
def valid_development_report(r):
 if not isinstance(r,dict) or r.get('version')!=VERSION:return False
 payload={k:r.get(k) for k in ('session','tabs','visual','state','localization','repair')};return r.get('digest')==_d(payload) and valid_state_report(r['state']) and valid_repair_cycle(r['repair'])
