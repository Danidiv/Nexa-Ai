from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
def compare_visual(baseline_hash,current_hash,threshold=0.0):
 same=baseline_hash==current_hash; payload={'baseline_hash':baseline_hash,'current_hash':current_hash,'threshold':float(threshold),'same':same}; return {'version':VERSION,**payload,'status':'match' if same else 'changed','difference':0.0 if same else 1.0,'digest':_d(payload)}
def valid_visual_diff(r): return isinstance(r,dict) and r.get('version')==VERSION and r.get('digest')==_d({k:r.get(k) for k in ('baseline_hash','current_hash','threshold','same')})
