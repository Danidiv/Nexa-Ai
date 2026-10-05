"""Setup 7.12: Backend Implementation Plan.
Plan backend services and handlers.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_backend_plan(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['targets', 'services', 'handlers']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "backend_plan", **values)

def valid_backend_plan(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "backend_plan" and obj.valid()
