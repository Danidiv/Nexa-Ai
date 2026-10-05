from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
def performance_report(metrics):
 safe={k:float(v) for k,v in metrics.items() if k in {'dom_content_loaded_ms','load_ms','first_contentful_paint_ms','transfer_bytes'}}; payload={'metrics':safe}; return {'version':VERSION,'metrics':safe,'status':'pass' if safe.get('load_ms',0)<=5000 else 'slow','digest':_d(payload)}
def valid_performance(r): return isinstance(r,dict) and r.get('version')==VERSION and r.get('digest')==_d({'metrics':r.get('metrics')})
