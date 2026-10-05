"""Setup 4.91: integrated codebase-intelligence contract and hardening."""
from __future__ import annotations
from hashlib import sha256
import json
VERSION=1

def build_intelligence_contract(index,search,graph,plan,symbols,references,selection,execution):
    payload={
        'index_digest':index.digest,'search':search,'graph_digest':graph.digest,
        'plan_digest':__import__('hashlib').sha256(json.dumps(plan.to_dict(),sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24],
        'symbol_digest':symbols.digest,'reference_digest':references.digest,
        'selection_digest':selection.digest,'execution_digest':execution.digest,
    }
    digest=sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
    return {'version':VERSION,'status':'ready','payload':payload,'digest':digest}

def validate_intelligence_contract(contract):
    if not isinstance(contract,dict) or contract.get('version')!=VERSION or contract.get('status')!='ready':return False
    p=contract.get('payload')
    if not isinstance(p,dict):return False
    expected=sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
    return expected==contract.get('digest') and all(isinstance(p.get(k),str) and p.get(k) for k in ('index_digest','graph_digest','plan_digest','symbol_digest','reference_digest','selection_digest','execution_digest'))
