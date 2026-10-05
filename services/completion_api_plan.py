"""Setup 7.13: API Implementation Plan.
Plan API routes, validation, and responses.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_api_plan(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['routes', 'validation', 'responses']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "api_plan", **values)

def valid_api_plan(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "api_plan" and obj.valid()
