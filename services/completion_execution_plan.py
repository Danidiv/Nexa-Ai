"""Setup 7.21: Execution Plan.
Turn implementation work into executable phases.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_execution_plan(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['steps', 'commands', 'gates']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "execution_plan", **values)

def valid_execution_plan(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "execution_plan" and obj.valid()
