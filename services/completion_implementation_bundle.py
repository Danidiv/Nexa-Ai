"""Setup 7.20: Full-Stack Implementation Bundle.
Combine implementation plans into one execution-ready bundle.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_implementation_bundle(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['frontend', 'backend', 'api', 'database', 'auth', 'ordering']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "implementation_bundle", **values)

def valid_implementation_bundle(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "implementation_bundle" and obj.valid()
