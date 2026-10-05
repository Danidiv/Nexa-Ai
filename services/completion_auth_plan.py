"""Setup 7.15: Authentication Implementation Plan.
Plan login, sessions, authorization, and safe credential handling.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_auth_plan(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['login', 'session', 'authorization']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "auth_plan", **values)

def valid_auth_plan(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "auth_plan" and obj.valid()
