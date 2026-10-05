"""Setup 4.96: integrated runtime intelligence contract and hardening."""
from __future__ import annotations
from hashlib import sha256
import json
from services.completion_runtime_intelligence import build_runtime_profile,RuntimeProfile
from services.completion_runtime_entrypoints import discover_entrypoints,EntryPointIndex
from services.completion_runtime_environment import build_environment_map,RuntimeEnvironment
from services.completion_runtime_verification import build_verification_plan,RuntimeVerificationPlan
VERSION=1
def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
def runtime_intelligence_report(root_dir):
 p=build_runtime_profile(root_dir); e=discover_entrypoints(root_dir,p); env=build_environment_map(root_dir,p); v=build_verification_plan(p,e,env)
 payload={'profile':p.to_dict(),'entrypoints':e.to_dict(),'environment':env.to_dict(),'verification':v.to_dict()}; digest=_digest(payload)
 return {'version':VERSION,'status':'ready' if all([p.valid(),e.valid(),env.valid(),v.valid(p,e,env)]) else 'blocked','profile':p.to_dict(),'entrypoints':e.to_dict(),'environment':env.to_dict(),'verification':v.to_dict(),'digest':digest}
def validate_runtime_report(report):
 if not isinstance(report,dict) or report.get('version')!=VERSION:return False
 p=RuntimeProfile.from_dict(report.get('profile'));e=EntryPointIndex.from_dict(report.get('entrypoints'));env=RuntimeEnvironment.from_dict(report.get('environment'));v=RuntimeVerificationPlan.from_dict(report.get('verification'))
 if not all([p,e,env,v]) or not all([p.valid(),e.valid(),env.valid(),v.valid(p,e,env)]):return False
 payload={'profile':p.to_dict(),'entrypoints':e.to_dict(),'environment':env.to_dict(),'verification':v.to_dict()}; return _digest(payload)==report.get('digest')
