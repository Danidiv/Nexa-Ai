from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
def build_flow_suite(steps):
 normalized=[{'index':i+1,'action':s['action'],'target':s.get('target'),'expected':s.get('expected')} for i,s in enumerate(steps)]; payload={'steps':normalized}; return {'version':VERSION,'steps':normalized,'status':'ready' if normalized else 'empty','digest':_d(payload)}
def valid_flow_suite(r): return isinstance(r,dict) and r.get('version')==VERSION and r.get('digest')==_d({'steps':r.get('steps')})
