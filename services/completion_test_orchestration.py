"""Setup 7.27: Test Orchestration Plan.
Prioritize and execute relevant tests.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_test_orchestration(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['suites', 'priority', 'stop_conditions']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "test_orchestration", **values)

def valid_test_orchestration(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "test_orchestration" and obj.valid()
