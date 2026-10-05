"""Setup 7.02: Requirement Normalization.
Normalize requirement language without losing intent.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_normalized_requirements(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['goal', 'features', 'constraints']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "normalized_requirements", **values)

def valid_normalized_requirements(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "normalized_requirements" and obj.valid()
