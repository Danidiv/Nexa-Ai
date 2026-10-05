from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def evaluate_release(checks):
    rows=[{"name":str(x.get("name")),"status":str(x.get("status"))} for x in (checks or [])]
    payload={"checks":rows}; blocked=any(x["status"] not in ("pass","stable") for x in rows)
    return {"version":VERSION,"checks":rows,"status":"blocked" if blocked else "ready","digest":_d(payload)}
def valid_release(r): return isinstance(r,dict) and r.get("version")==VERSION and r.get("digest")==_d({"checks":r.get("checks")})
