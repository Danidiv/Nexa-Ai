"""Setup 7.36: API Browser Verification.
Verify browser-visible API behavior and error handling.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_api_browser(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['requests', 'responses', 'errors']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "api_browser", **values)

def valid_api_browser(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "api_browser" and obj.valid()
