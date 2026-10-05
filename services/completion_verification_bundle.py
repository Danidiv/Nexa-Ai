"""Setup 7.40: Product Verification Bundle.
Combine browser, visual, runtime, and flow verification.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_verification_bundle(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['browser', 'visual', 'console', 'flows']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "verification_bundle", **values)

def valid_verification_bundle(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "verification_bundle" and obj.valid()
