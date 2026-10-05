"""Setup 7.41: Autonomous Repair Coordinator.
Coordinate evidence-driven repairs across layers.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_repair_coordinator(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['issues', 'candidates', 'ordering']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "repair_coordinator", **values)

def valid_repair_coordinator(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "repair_coordinator" and obj.valid()
