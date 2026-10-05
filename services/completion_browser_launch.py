"""Setup 7.31: Browser Launch Verification.
Verify the application is reachable in a browser runtime.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_browser_launch(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['url', 'status', 'readiness']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "browser_launch", **values)

def valid_browser_launch(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "browser_launch" and obj.valid()
