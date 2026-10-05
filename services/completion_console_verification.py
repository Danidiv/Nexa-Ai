"""Setup 7.38: Runtime Console Verification.
Collect and classify browser console failures.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_console_verification(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['errors', 'warnings', 'source']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "console_verification", **values)

def valid_console_verification(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "console_verification" and obj.valid()
