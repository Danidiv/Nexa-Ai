"""Setup 9.00 integrated Product Builder V4."""
from .phase8_ext_runtime import artifact,merge,unique,risk,topo
def build_900(task_id,*,product=None,implementation=None,release=None,operations=None,feedback=None,security=None,risk_level="low"):
    risk(risk_level)
    product=merge(product or {}); implementation=merge(implementation or {}); release=merge(release or {}); operations=merge(operations or {}); feedback=merge(feedback or {}); security=merge(security or {})
    plan=implementation.get("plan",{})
    if plan.get("nodes"): topo(plan["nodes"],plan.get("edges",[]))
    return artifact("9.00",task_id,"Integrated Lovable-Level Product Builder V4",product=product,implementation=implementation,release=release,operations=operations,feedback=feedback,security=security,risk=risk_level)
def valid_900(obj): return obj.setup=="9.00" and obj.kind=="Integrated Lovable-Level Product Builder V4" and obj.valid()
