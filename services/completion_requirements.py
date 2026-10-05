"""Setup 7.01: Requirement Intake.
Capture a product request as bounded, structured requirements.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_requirements(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['intent', 'constraints', 'acceptance']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "requirements", **values)

def valid_requirements(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "requirements" and obj.valid()
