from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
def coordinate_qa(url,accessibility,visual,performance):
 payload={'url':url,'accessibility':accessibility,'visual':visual,'performance':performance}; ok=accessibility.get('status')=='pass' and visual.get('status')=='match' and performance.get('status')=='pass'; return {'version':VERSION,'status':'pass' if ok else 'issues','url':url,'checks':{'accessibility':accessibility.get('status'),'visual':visual.get('status'),'performance':performance.get('status')},'digest':_d(payload)}
def valid_qa(r,a,v,p): return isinstance(r,dict) and r.get('version')==VERSION and r.get('digest')==_d({'url':r.get('url'),'accessibility':a,'visual':v,'performance':p})
