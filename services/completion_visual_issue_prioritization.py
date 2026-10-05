from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def prioritize(issues):
    rows=[]
    for i,x in enumerate(issues or []):
        sev=str(x.get("severity","medium")); impact={"critical":4,"high":3,"medium":2,"low":1}.get(sev,2)
        rows.append({"id":str(x.get("id",i+1)),"severity":sev,"impact":impact,"category":str(x.get("category","unknown"))})
    rows.sort(key=lambda x:(-x["impact"],x["id"]))
    payload={"issues":rows}; return {"version":VERSION,"issues":rows,"status":"blocked" if any(x["severity"]=="critical" for x in rows) else ("issues" if rows else "pass"),"digest":_d(payload)}
def valid_priorities(r):
    return isinstance(r,dict) and r.get("version")==VERSION and r.get("digest")==_d({"issues":r.get("issues")})
