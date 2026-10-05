"""Setup 4.73: cross-layer terminal identity consistency."""
from hashlib import sha256
import json
def _digest(parts): return sha256(json.dumps(parts,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
def check_consistency(resolution=None,machine=None,recovery=None,epoch=0):
 if resolution is None and machine is None and recovery is None:return {"status":"not_required","digest":""}
 checks=[]
 if resolution is not None: checks += [getattr(resolution,"valid",lambda:False)(), getattr(resolution,"change_epoch",epoch)==epoch]
 if machine is not None: checks += [getattr(machine,"valid_state",lambda:False)(), getattr(machine,"state","") not in {"BLOCKED","DONE"} or getattr(machine,"state","")=="DONE"]
 if recovery is not None: checks += [getattr(recovery,"valid",lambda:False)(), getattr(recovery,"change_epoch",epoch)==epoch]
 return {"status":"consistent" if all(checks) else "inconsistent","digest":_digest({"epoch":epoch,"resolution":getattr(resolution,"resolution_id","") if resolution else "","machine":getattr(machine,"sequence",0) if machine else 0,"recovery":getattr(recovery,"recovery_id","") if recovery else ""})}
