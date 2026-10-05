from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def inspect_mobile(targets):
    rows=[{"selector":str(x.get("selector")),"width":int(x.get("width",44)),"height":int(x.get("height",44)),"tap_target":"pass" if int(x.get("width",44))>=44 and int(x.get("height",44))>=44 else "fail"} for x in (targets or [])]
    payload={"targets":rows}; return {"version":VERSION,"targets":rows,"status":"pass" if all(x["tap_target"]=="pass" for x in rows) else "issues","digest":_d(payload)}
def valid_mobile(r): return isinstance(r,dict) and r.get("version")==VERSION and r.get("digest")==_d({"targets":r.get("targets")})
