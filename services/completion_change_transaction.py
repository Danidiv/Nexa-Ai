"""Setup 7.24: Change Transaction Plan.
Plan atomic multi-file changes with rollback boundaries.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_change_transaction(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['files', 'commit_points', 'rollback']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "change_transaction", **values)

def valid_change_transaction(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "change_transaction" and obj.valid()
