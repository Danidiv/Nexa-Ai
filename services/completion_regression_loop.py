"""Setup 7.43: Regression Repair Loop.
Re-test after repair and detect regressions.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_regression_loop(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['repair', 'tests', 'regressions']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "regression_loop", **values)

def valid_regression_loop(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "regression_loop" and obj.valid()
