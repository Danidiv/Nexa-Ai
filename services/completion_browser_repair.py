"""Setup 5.89: autonomous browser repair loop contract."""
from hashlib import sha256
import json
VERSION=1;MAX_CYCLES=5
def _d(p):return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def build_repair_cycle(error,localization,changes=None):
 p={'error':str(error),'candidates':localization.get('candidates',[])[:8],'changes':list(changes or [])[:16],'steps':['diagnose','localize','repair','refresh','verify']};return {'version':VERSION,**p,'digest':_d(p)}
def valid_repair_cycle(r):
 p={k:r.get(k) for k in ('error','candidates','changes','steps')};return r.get('version')==VERSION and r.get('digest')==_d(p)
def advance_cycle(cycle,result):
 cycle=dict(cycle); cycle['last_result']=result; cycle['steps']=list(cycle.get('steps',[])); return cycle
