"""Setup 7.32: Page Navigation Verification.
Verify required routes and navigation behavior.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_page_navigation(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['routes', 'navigation', 'failures']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "page_navigation", **values)

def valid_page_navigation(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "page_navigation" and obj.valid()
