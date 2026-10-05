from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def build_repair_plan(reports):
    actions=[]
    for r in reports or []:
        if r.get("status") not in ("pass","stable"):
            actions.append({"source":str(r.get("source")),"action":"repair","reason":str(r.get("status"))})
    payload={"actions":actions,"sources":[str(r.get("source")) for r in reports or []]}; return {"version":VERSION,"actions":actions,"sources":payload["sources"],"digest":_d(payload)}
def valid_repair_plan(r): return isinstance(r,dict) and r.get("version")==VERSION and r.get("digest")==_d({"actions":r.get("actions"),"sources":r.get("sources")})
