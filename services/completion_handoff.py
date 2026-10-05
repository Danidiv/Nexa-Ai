"""Setup 7.46: Project Handoff Package.
Create a reproducible engineering handoff package.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_handoff(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['summary', 'changes', 'verification']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "handoff", **values)

def valid_handoff(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "handoff" and obj.valid()
