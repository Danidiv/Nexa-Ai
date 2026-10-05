"""Setup 7.34: Form Flow Verification.
Verify form submission, validation, and feedback.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_form_flow(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['fields', 'validation', 'submission']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "form_flow", **values)

def valid_form_flow(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "form_flow" and obj.valid()
