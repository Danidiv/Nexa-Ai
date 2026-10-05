"""Setup 7.33: UI Interaction Verification.
Verify critical user interactions and controls.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_ui_interaction(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['actions', 'expected', 'evidence']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "ui_interaction", **values)

def valid_ui_interaction(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "ui_interaction" and obj.valid()
