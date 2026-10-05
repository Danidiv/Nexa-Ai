"""Setup 7.05: Architecture Discovery.
Infer application layers and integration boundaries.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_architecture_discovery(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['frontend', 'backend', 'database']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "architecture_discovery", **values)

def valid_architecture_discovery(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "architecture_discovery" and obj.valid()
