"""Setup 7.11: Frontend Implementation Plan.
Plan frontend changes from understood requirements.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_frontend_plan(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['targets', 'components', 'state']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "frontend_plan", **values)

def valid_frontend_plan(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "frontend_plan" and obj.valid()
