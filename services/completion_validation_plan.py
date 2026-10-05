"""Setup 7.18: Validation Implementation Plan.
Plan input and business-rule validation.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_validation_plan(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['client', 'server', 'rules']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "validation_plan", **values)

def valid_validation_plan(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "validation_plan" and obj.valid()
