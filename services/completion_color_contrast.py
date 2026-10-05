from hashlib import sha256
import json,re
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def inspect_contrast(samples):
    rows=[]
    for s in samples or []:
        ratio=float(s.get("ratio",0)); level="AAA" if ratio>=7 else ("AA" if ratio>=4.5 else "fail")
        rows.append({"name":str(s.get("name","sample")),"ratio":ratio,"level":level})
    payload={"samples":rows}; return {"version":VERSION,"samples":rows,"status":"pass" if all(x["level"]!="fail" for x in rows) else "issues","digest":_d(payload)}
def valid_contrast(r): return isinstance(r,dict) and r.get("version")==VERSION and r.get("digest")==_d({"samples":r.get("samples")})
