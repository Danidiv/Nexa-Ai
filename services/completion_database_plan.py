"""Setup 7.14: Database Implementation Plan.
Plan schema and migration changes.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_database_plan(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['tables', 'migrations', 'indexes']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "database_plan", **values)

def valid_database_plan(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "database_plan" and obj.valid()
