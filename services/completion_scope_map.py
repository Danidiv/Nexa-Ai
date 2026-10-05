"""Setup 7.03: Product Scope Mapping.
Map requested scope into in-scope and out-of-scope areas.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_scope_map(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['in_scope', 'out_of_scope', 'assumptions']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "scope_map", **values)

def valid_scope_map(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "scope_map" and obj.valid()
