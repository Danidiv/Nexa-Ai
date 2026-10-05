"""Setup 4.89: intelligent change-target selection from symbols and references."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json
VERSION=1; MAX_TARGETS=16

@dataclass
class ChangeSelection:
    query:str; targets:list[str]; reasons:dict[str,list[str]]; digest:str
    def to_dict(self):d=asdict(self);d['change_selection_version']=VERSION;return d
    def valid(self):
        payload={'query':self.query,'targets':self.targets,'reasons':self.reasons}
        expected=sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
        return expected==self.digest
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or d.get('change_selection_version')!=VERSION:return None
        try:return cls(str(d.get('query','')),[str(x) for x in d.get('targets',[])][:MAX_TARGETS],{str(k):[str(x) for x in v] for k,v in (d.get('reasons') or {}).items()},str(d.get('digest','')))
        except Exception:return None

def select_change_targets(query,search_results,symbol_index,reference_index):
    q=str(query).lower(); scored={}; reasons={}
    for r in search_results:
        p=str(r.get('path','')); score=int(r.get('score',0));
        if p: scored[p]=max(scored.get(p,0),score); reasons.setdefault(p,[]).append('direct search hit')
    for s in symbol_index.symbols:
        name=str(s.get('name','')); p=str(s.get('path',''))
        if p and any(t in name.lower() for t in q.split() if len(t)>1):
            scored[p]=scored.get(p,0)+3; reasons.setdefault(p,[]).append('symbol name matches query')
    for r in reference_index.references:
        if r.get('source') in scored:
            t=str(r.get('target','')); scored[t]=scored.get(t,0)+1; reasons.setdefault(t,[]).append('referenced by selected target')
    ordered=sorted(scored,key=lambda p:(-scored[p],p))[:MAX_TARGETS]
    payload={'query':q[:160],'targets':ordered,'reasons':{p:reasons[p] for p in ordered}}
    dig=sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
    return ChangeSelection(q[:160],ordered,payload['reasons'],dig)
