"""Setup 7.29: Long Task Checkpoint.
Checkpoint long-running product builds for safe recovery.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_long_task_checkpoint(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['checkpoint', 'resume', 'state']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "long_task_checkpoint", **values)

def valid_long_task_checkpoint(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "long_task_checkpoint" and obj.valid()
