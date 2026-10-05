"""Setup 4.71: durable terminal resolution state transitions."""
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
VERSION=1
STATES={"not_required","ready","resume_verification","quarantine","invalid"}
TRANSITIONS={"not_required":{"ready","resume_verification","quarantine","invalid","not_required"},"ready":{"not_required","ready"},"resume_verification":{"resume_verification","ready","quarantine","invalid"},"quarantine":{"quarantine","invalid","not_required"},"invalid":{"invalid","not_required"}}
def _seal(r): return sha256(json.dumps({"v":VERSION,**{k:getattr(r,k) for k in ("status","resolution_id","previous_status","reason_code","change_epoch")}},sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
@dataclass
class TerminalResolutionState:
 status:str="not_required"; resolution_id:str=""; previous_status:str=""; reason_code:str=""; change_epoch:int=0; seal:str=""
 def to_dict(self): return {**asdict(self),"terminal_resolution_state_version":VERSION}
 @classmethod
 def from_dict(cls,d):
  if not isinstance(d,dict) or d.get("terminal_resolution_state_version",VERSION)!=VERSION:return None
  try:return cls(status=str(d.get("status") or "not_required"),resolution_id=str(d.get("resolution_id") or ""),previous_status=str(d.get("previous_status") or ""),reason_code=str(d.get("reason_code") or ""),change_epoch=max(0,int(d.get("change_epoch",0) or 0)),seal=str(d.get("seal") or ""))
  except (TypeError,ValueError):return None
 def valid(self):
  if self.status=="not_required": return not self.resolution_id and not self.seal
  return self.status in STATES and bool(self.resolution_id and self.reason_code and self.seal) and _seal(self)==self.seal
 def transition(self,new_status,reason="state_transition",epoch=None):
  if new_status not in STATES or new_status not in TRANSITIONS.get(self.status,set()): return False
  self.previous_status=self.status; self.status=new_status; self.reason_code=str(reason); self.change_epoch=max(0,int(self.change_epoch if epoch is None else epoch)); self.resolution_id=sha256(f"{self.status}|{self.previous_status}|{self.reason_code}|{self.change_epoch}".encode()).hexdigest()[:24]; self.seal=_seal(self); return True
