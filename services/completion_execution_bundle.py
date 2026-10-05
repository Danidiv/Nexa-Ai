"""Setup 7.30: Autonomous Execution Bundle.
Combine execution, safety, testing, and recovery controls.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_execution_bundle(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['plan', 'tools', 'transactions', 'tests', 'recovery']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "execution_bundle", **values)

def valid_execution_bundle(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "execution_bundle" and obj.valid()
