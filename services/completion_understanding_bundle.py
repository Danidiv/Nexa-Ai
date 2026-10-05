"""Setup 7.10: Product Understanding Bundle.
Combine product understanding artifacts into one sealed bundle.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_understanding_bundle(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['requirements', 'scope', 'architecture', 'ui', 'api', 'data']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "understanding_bundle", **values)

def valid_understanding_bundle(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "understanding_bundle" and obj.valid()
