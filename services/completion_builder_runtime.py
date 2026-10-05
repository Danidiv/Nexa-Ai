"""Setup 7.49: Product Builder Runtime.
Coordinate the product-builder lifecycle without bypassing existing runtime controls.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_builder_runtime(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['phases', 'state', 'evidence']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "builder_runtime", **values)

def valid_builder_runtime(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "builder_runtime" and obj.valid()
