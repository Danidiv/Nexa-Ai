from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def detect_flaky(runs):
    groups={}
    for x in runs or []: groups.setdefault(str(x.get("name")),[]).append(str(x.get("status")))
    rows=[{"name":k,"statuses":v,"flaky":("pass" in v and "fail" in v)} for k,v in sorted(groups.items())]
    payload={"tests":rows}; return {"version":VERSION,"tests":rows,"status":"flaky" if any(x["flaky"] for x in rows) else "stable","digest":_d(payload)}
def valid_flaky(r): return isinstance(r,dict) and r.get("version")==VERSION and r.get("digest")==_d({"tests":r.get("tests")})
