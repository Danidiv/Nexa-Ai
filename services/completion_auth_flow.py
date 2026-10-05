"""Setup 7.35: Authentication Flow Verification.
Verify login and protected-route behavior.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_auth_flow(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['login', 'protected_routes', 'logout']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "auth_flow", **values)

def valid_auth_flow(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "auth_flow" and obj.valid()
