"""Setup 7.17: UI State Implementation Plan.
Plan loading, empty, error, and success UI states.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_ui_state_plan(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['loading', 'empty', 'error']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "ui_state_plan", **values)

def valid_ui_state_plan(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "ui_state_plan" and obj.valid()
