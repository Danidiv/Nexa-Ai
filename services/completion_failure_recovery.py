"""Setup 7.28: Failure Recovery Plan.
Plan evidence-driven recovery after execution failures.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_failure_recovery(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['failure_classes', 'repairs', 'retry_limits']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "failure_recovery", **values)

def valid_failure_recovery(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "failure_recovery" and obj.valid()
