"""Setup 7.45: Release Candidate Builder.
Assemble a verified release candidate manifest.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_release_candidate(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['artifacts', 'checks', 'status']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "release_candidate", **values)

def valid_release_candidate(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "release_candidate" and obj.valid()
