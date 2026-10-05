"""Setup 7.47: Autonomous Product Session.
Represent one end-to-end autonomous product-building session.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_product_session(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['understanding', 'implementation', 'execution', 'verification']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "product_session", **values)

def valid_product_session(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "product_session" and obj.valid()
