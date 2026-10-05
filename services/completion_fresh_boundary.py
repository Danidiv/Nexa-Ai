"""Setup 4.75: fresh-completion boundary for stale terminal artifacts."""
from hashlib import sha256
def artifact_epoch(*records):
 vals=[max(0,int(getattr(r,"change_epoch",0) or 0)) for r in records if r is not None]; return max(vals) if vals else 0
def fresh_for_epoch(record,current_epoch):
 return record is not None and max(0,int(getattr(record,"change_epoch",0) or 0))==max(0,int(current_epoch or 0)) and bool(getattr(record,"valid",lambda:False)())
def boundary_digest(epoch,reason): return sha256(f"{max(0,int(epoch or 0))}|{reason}".encode()).hexdigest()[:24]
def requires_fresh_completion(status): return status in {"quarantine","invalid","stale"}
