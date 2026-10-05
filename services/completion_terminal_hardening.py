"""Setup 4.81: end-to-end terminal hardening contract."""
from hashlib import sha256
import json
REQUIRED=("ledger","snapshot","replay","recovery")
def hardening_digest(report): return sha256(json.dumps(report,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
def build_report(*,ledger_valid,snapshot_valid,replay_valid,recovery_valid,epoch_aligned=True):
 checks={"ledger":bool(ledger_valid),"snapshot":bool(snapshot_valid),"replay":bool(replay_valid),"recovery":bool(recovery_valid),"epoch_aligned":bool(epoch_aligned)}
 return {"version":1,"status":"hardened" if all(checks.values()) else "blocked","checks":checks,"digest":hardening_digest(checks)}
def validate_report(report):
 if not isinstance(report,dict) or report.get("version")!=1:return False
 checks=report.get("checks");
 if not isinstance(checks,dict) or any(k not in checks for k in REQUIRED+('epoch_aligned',)):return False
 if report.get("status") not in {"hardened","blocked"}:return False
 if report.get("status")=="hardened" and not all(bool(v) for v in checks.values()):return False
 if report.get("status")=="blocked" and all(bool(v) for v in checks.values()):return False
 return report.get("digest")==hardening_digest(checks)
