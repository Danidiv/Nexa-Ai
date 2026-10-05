"""Setup 5.84: visual element targeting."""
from hashlib import sha256
import json
VERSION=1
def _d(p):return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def target_element(model,description):
    q=str(description).strip().lower(); ranked=[]
    for e in model.elements:
        score=0; text=str(e.text).lower(); tag=e.tag.lower()
        if q and q in text:score+=4
        if q==tag:score+=2
        if q in str(e.selector).lower():score+=3
        if score:ranked.append((score,e))
    ranked.sort(key=lambda x:(-x[0],x[1].element_id));
    if not ranked:return {'status':'not_found','description':q,'selector':'','confidence':0.0,'digest':_d({'status':'not_found','description':q,'selector':'','confidence':0.0})}
    e=ranked[0][1]; conf=min(1.0,0.5+ranked[0][0]*0.1); p={'status':'matched','description':q,'selector':e.selector,'element_id':e.element_id,'confidence':conf}; return {**p,'digest':_d(p)}
def valid_target(t):
    p={k:t.get(k) for k in ('status','description','selector','element_id','confidence') if k in t}; return t.get('digest')==_d(p)
