"""Setup 4.76: batch hardening utilities for the terminal completion chain."""
from hashlib import sha256
import json
MAX_HISTORY=64
MAX_ID_LEN=24
def bounded_history(values): return list(values or [])[-MAX_HISTORY:]
def canonical_digest(value): return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:MAX_ID_LEN]
def hardening_report(*checks):
 vals=[bool(x) for x in checks]; return {"status":"hardened" if all(vals) else "blocked","checks":len(vals),"passed":sum(vals)}
