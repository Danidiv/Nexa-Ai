"""Setup 8.50 integrated Lovable-level Product Builder V3."""
from .phase8_runtime import artifact, topological, merge_context, unique_text, score_risk

def build_850(task_id, *, requirements=None, architecture=None, plan=None, qa=None, evidence=None, risk="low"):
    score_risk(risk)
    requirements=merge_context(requirements or {})
    architecture=merge_context(architecture or {})
    plan=merge_context(plan or {})
    qa=merge_context(qa or {})
    evidence=unique_text(evidence or [])
    nodes=plan.get("nodes",[])
    edges=plan.get("edges",[])
    if nodes: topological(nodes, edges)
    return artifact("8.50", task_id, "Integrated Lovable-Level Product Builder V3", requirements=requirements, architecture=architecture, plan=plan, qa=qa, evidence=evidence, risk=risk)

def valid_850(obj):
    return obj.setup=="8.50" and obj.kind=="Integrated Lovable-Level Product Builder V3" and obj.valid()
