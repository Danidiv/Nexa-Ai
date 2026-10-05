"""Setup 5.06: browser interaction execution boundary.
Supports a driver protocol: driver.execute(action_dict) -> evidence dict. No fake success is produced.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
VERSION=1; MAX_ACTIONS=32

def _digest(p):return sha256(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:24]
@dataclass
class ActionExecution:
    action:dict; success:bool; evidence:dict; error:str=''; digest:str=''
    def seal(self):self.digest=_digest({'action':self.action,'success':self.success,'evidence':self.evidence,'error':self.error});return self
    def to_dict(self):d=asdict(self);d['browser_actions_version']=VERSION;return d
    def valid(self):return self.digest==_digest({'action':self.action,'success':self.success,'evidence':self.evidence,'error':self.error})

def execute_action(driver,action):
    if not isinstance(action,dict) or not action.get('action'):return ActionExecution(action or {},False,{},'invalid action').seal()
    try:
        evidence=driver.execute(dict(action))
        if not isinstance(evidence,dict):return ActionExecution(action,False,{},'driver returned invalid evidence').seal()
        success=bool(evidence.get('success',False))
        return ActionExecution(action,success,evidence,'' if success else str(evidence.get('error','action failed'))).seal()
    except Exception as e:return ActionExecution(action,False,{},f'{type(e).__name__}: {e}').seal()

def execute_flow(driver,actions):
    out=[]
    for action in list(actions or [])[:MAX_ACTIONS]:
        r=execute_action(driver,action);out.append(r.to_dict())
        if not r.success:break
    return out
