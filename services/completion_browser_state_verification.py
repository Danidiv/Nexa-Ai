"""Setup 5.87: browser state verification."""
from hashlib import sha256
import json
def _d(p):return sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:24]
def verify_state(actual,expected):
 checks={};
 for k,v in expected.items():checks[k]=actual.get(k)==v
 p={'checks':checks,'passed':all(checks.values())};return {**p,'digest':_d(p)}
def valid_state_report(r):
 p={'checks':r.get('checks',{}),'passed':r.get('passed',False)};return r.get('digest')==_d(p)
