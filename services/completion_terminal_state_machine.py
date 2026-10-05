"""Setup 4.72: explicit terminal completion state machine."""
from dataclasses import dataclass
STATES=("IDLE","VERIFYING","RESOLVING","AUTHORIZED","EMITTING","AUDITED","BLOCKED","DONE")
ALLOWED={"IDLE":{"VERIFYING"},"VERIFYING":{"RESOLVING","BLOCKED"},"RESOLVING":{"AUTHORIZED","BLOCKED"},"AUTHORIZED":{"EMITTING","BLOCKED"},"EMITTING":{"AUDITED","BLOCKED"},"AUDITED":{"DONE","BLOCKED"},"BLOCKED":{"VERIFYING"},"DONE":set()}
@dataclass
class TerminalStateMachine:
 state:str="IDLE"
 sequence:int=0
 def valid_state(self): return self.state in STATES and self.sequence>=0
 def transition(self,target):
  if target not in ALLOWED.get(self.state,set()): return False
  self.state=target; self.sequence+=1; return True
 def can_finalize(self): return self.state=="DONE"
 def to_dict(self): return {"version":1,"state":self.state,"sequence":self.sequence}
 @classmethod
 def from_dict(cls,d):
  if not isinstance(d,dict) or d.get("version",1)!=1:return None
  try:r=cls(str(d.get("state","IDLE")),int(d.get("sequence",0))); return r if r.valid_state() else None
  except (TypeError,ValueError):return None
