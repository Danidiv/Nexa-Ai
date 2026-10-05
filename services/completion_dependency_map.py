"""Setup 7.09: Dependency Mapping.
Map runtime and development dependencies to product needs.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_dependency_map(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['runtime', 'development', 'external']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "dependency_map", **values)

def valid_dependency_map(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "dependency_map" and obj.valid()
