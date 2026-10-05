from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def inspect_network(requests):
    rows=[{"url":str(x.get("url")),"status":int(x.get("status",0)),"duration_ms":float(x.get("duration_ms",0))} for x in (requests or [])]
    payload={"requests":rows}; ok=all(200<=x["status"]<400 and x["duration_ms"]<=3000 for x in rows)
    return {"version":VERSION,"requests":rows,"status":"pass" if ok else "issues","digest":_d(payload)}
def valid_network(r): return isinstance(r,dict) and r.get("version")==VERSION and r.get("digest")==_d({"requests":r.get("requests")})
