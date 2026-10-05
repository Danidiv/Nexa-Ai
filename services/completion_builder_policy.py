"""Setup 7.48: Product Builder Policy.
Define safe autonomous product-builder policies.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_builder_policy(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['permissions', 'stop_conditions', 'human_escalation']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "builder_policy", **values)

def valid_builder_policy(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "builder_policy" and obj.valid()
