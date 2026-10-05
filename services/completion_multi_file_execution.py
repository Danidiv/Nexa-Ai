"""Setup 4.90: safe multi-file execution orchestration plan.

Planning only: this layer does not write files or execute commands.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
VERSION=1; MAX_FILES=24

@dataclass
class ExecutionStage:
    name:str; paths:list[str]; required:bool=True
    def to_dict(self):return asdict(self)

@dataclass
class MultiFileExecutionPlan:
    targets:list[str]; stages:list[dict]; digest:str
    def to_dict(self):d=asdict(self);d['multi_file_execution_version']=VERSION;return d
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get('multi_file_execution_version')!=VERSION:return None
        try:return cls([str(x) for x in d.get('targets',[])][:MAX_FILES],[dict(x) for x in d.get('stages',[])][:8],str(d.get('digest','')))
        except Exception:return None

def build_execution_plan(selection,code_change_plan):
    targets=list(dict.fromkeys([str(x) for x in selection.targets]))[:MAX_FILES]
    inspect=[str(x) for x in code_change_plan.inspect if str(x) not in targets][:MAX_FILES]
    verify=list(dict.fromkeys([str(x) for x in code_change_plan.verify]+targets))[:MAX_FILES]
    stages=[ExecutionStage('inspect',inspect+targets),ExecutionStage('change',targets),ExecutionStage('verify',verify)]
    rows=[s.to_dict() for s in stages]; payload={'targets':targets,'stages':rows}
    dig=sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
    return MultiFileExecutionPlan(targets,rows,dig)
