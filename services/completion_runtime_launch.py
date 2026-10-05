"""Setup 7.26: Runtime Launch Plan.
Plan application startup and readiness detection.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_runtime_launch(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['command', 'ports', 'readiness']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "runtime_launch", **values)

def valid_runtime_launch(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "runtime_launch" and obj.valid()
