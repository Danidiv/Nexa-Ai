"""Setup 7.37: Visual Regression Verification.
Compare visual checkpoints and identify meaningful differences.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_visual_regression(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['baselines', 'screens', 'differences']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "visual_regression", **values)

def valid_visual_regression(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "visual_regression" and obj.valid()
