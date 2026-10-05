"""Setup 7.16: Integration Implementation Plan.
Plan external service and internal integration work.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_integration_plan(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['integrations', 'adapters', 'fallbacks']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "integration_plan", **values)

def valid_integration_plan(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "integration_plan" and obj.valid()
