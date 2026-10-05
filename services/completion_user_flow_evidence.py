"""Setup 7.39: User Flow Evidence.
Assemble evidence for critical user journeys.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_user_flow_evidence(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['flows', 'checkpoints', 'evidence']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "user_flow_evidence", **values)

def valid_user_flow_evidence(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "user_flow_evidence" and obj.valid()
