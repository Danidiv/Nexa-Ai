"""Setup 4.79: terminal transition replay protection."""
from hashlib import sha256
import json
MAX_SEEN=128
def transition_id(sequence,source,target,reason):
 return sha256(json.dumps({"sequence":int(sequence),"source":str(source),"target":str(target),"reason":str(reason)},sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
class ReplayGuard:
 def __init__(self,seen=None): self.seen=list(seen or [])[-MAX_SEEN:]
 def accept(self,sequence,source,target,reason):
  tid=transition_id(sequence,source,target,reason)
  if tid in self.seen:return False
  self.seen.append(tid); self.seen=self.seen[-MAX_SEEN:]; return True
 def valid(self): return len(self.seen)==len(set(self.seen)) and len(self.seen)<=MAX_SEEN
 def to_dict(self): return {"version":1,"seen":list(self.seen)}
 @classmethod
 def from_dict(cls,d):
  if not isinstance(d,dict) or d.get("version",1)!=1:return None
  r=cls(d.get("seen",[])); return r if r.valid() else None
