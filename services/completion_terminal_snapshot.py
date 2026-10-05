"""Setup 4.78: integrity-protected terminal state snapshots."""
from dataclasses import dataclass
from hashlib import sha256
import json
VERSION=1
def snapshot_digest(state,sequence,ledger_head,epoch):
 return sha256(json.dumps({"v":VERSION,"state":state,"sequence":int(sequence),"ledger_head":ledger_head,"epoch":int(epoch)},sort_keys=True,separators=(",",":" )).encode()).hexdigest()[:24]
@dataclass
class TerminalSnapshot:
 state:str="IDLE"; sequence:int=0; ledger_head:str=""; epoch:int=0; digest:str=""
 def seal(self): self.digest=snapshot_digest(self.state,self.sequence,self.ledger_head,self.epoch); return self
 def valid(self): return self.digest==snapshot_digest(self.state,self.sequence,self.ledger_head,self.epoch)
 def to_dict(self): return {"version":VERSION,"state":self.state,"sequence":self.sequence,"ledger_head":self.ledger_head,"epoch":self.epoch,"digest":self.digest}
 @classmethod
 def from_dict(cls,d):
  if not isinstance(d,dict) or d.get("version",VERSION)!=VERSION:return None
  try:
   r=cls(str(d.get("state","IDLE")),int(d.get("sequence",0)),str(d.get("ledger_head","")),int(d.get("epoch",0)),str(d.get("digest",""))); return r if r.valid() else None
  except (TypeError,ValueError):return None
