"""Setup 4.80: deterministic coordinator for terminal recovery."""
from dataclasses import dataclass
from hashlib import sha256
import json
STATES=("IDLE","VERIFYING","RESOLVING","AUTHORIZED","EMITTING","AUDITED","DONE","BLOCKED")
@dataclass
class RecoveryDecision:
 action:str; reason:str; state:str; epoch:int; digest:str=""
 def seal(self):
  self.digest=sha256(json.dumps({"action":self.action,"reason":self.reason,"state":self.state,"epoch":self.epoch},sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]; return self
 def valid(self): return self.action in {"resume_verification","finalize","fresh_completion","clear"} and self.state in STATES and self.epoch>=0 and self.digest==sha256(json.dumps({"action":self.action,"reason":self.reason,"state":self.state,"epoch":self.epoch},sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
def coordinate(state,recovery_status,epoch=0):
 state=str(state); recovery_status=str(recovery_status); epoch=max(0,int(epoch))
 if recovery_status=="pending": a="resume_verification"; r="pending_emission"
 elif recovery_status=="orphaned": a="fresh_completion"; r="orphaned_emission"
 elif recovery_status=="reconciled" and state=="DONE": a="finalize"; r="reconciled_terminal"
 elif recovery_status in {"not_required",""} and state=="DONE": a="finalize"; r="clean_terminal"
 else: a="clear"; r="no_terminal_recovery_required"
 return RecoveryDecision(a,r,state,epoch).seal()
