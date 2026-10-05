"""Setup 4.74: crash/restart recovery classification for terminal state."""
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
@dataclass
class CrashRecovery:
 status:str="not_required"; source_state:str=""; resume_action:str=""; epoch:int=0; seal:str=""
 def seal_self(self): self.seal=sha256(json.dumps(asdict(self),sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
 def valid(self):
  if self.status=="not_required":return not self.seal
  if self.status not in {"resume","quarantine","clear"} or not self.resume_action or not self.seal:return False
  old=self.seal; self.seal=""; self.seal_self(); ok=self.seal==old; self.seal=old; return ok
def classify_crash(machine_state,recovery_status):
 if machine_state=="DONE":return CrashRecovery("clear",machine_state,"clear_terminal_state")
 if recovery_status=="pending":return CrashRecovery("resume",machine_state,"resume_verification")
 if recovery_status=="orphaned":return CrashRecovery("quarantine",machine_state,"require_fresh_completion")
 return CrashRecovery("clear",machine_state,"restart_verification")
