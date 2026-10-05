"""Setup 7.07: API Surface Mapping.
Represent API endpoints and their intended operations.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_api_surface(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['endpoints', 'auth', 'contracts']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "api_surface", **values)

def valid_api_surface(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "api_surface" and obj.valid()
