"""Setup 7.04: Project Discovery.
Describe the existing project structure and relevant entry points.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_project_discovery(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['root', 'files', 'entry_points']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "project_discovery", **values)

def valid_project_discovery(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "project_discovery" and obj.valid()
