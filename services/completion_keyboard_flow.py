from hashlib import sha256
import json
VERSION=1
def _d(p): return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def inspect_keyboard(elements):
    rows=[{"selector":str(x.get("selector")),"focusable":bool(x.get("focusable",False)),"label":bool(x.get("label",False))} for x in (elements or [])]
    payload={"elements":rows}; ok=all(x["focusable"] and x["label"] for x in rows)
    return {"version":VERSION,"elements":rows,"status":"pass" if ok else "issues","digest":_d(payload)}
def valid_keyboard(r): return isinstance(r,dict) and r.get("version")==VERSION and r.get("digest")==_d({"elements":r.get("elements")})
