from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def inspect_ux(html):
    h=html.lower(); checks={"heading":h.count("<h1")>0,"main":("<main" in h),"nav":("<nav" in h),"title":("<title" in h)}
    payload={"length":len(html),"checks":checks}; return {"version":VERSION,"length":len(html),"checks":checks,"status":"pass" if all(checks.values()) else "issues","digest":_d(payload)}
def valid_ux(r): return isinstance(r,dict) and r.get("version")==VERSION and r.get("digest")==_d({"length":r.get("length",0),"checks":r.get("checks")})
