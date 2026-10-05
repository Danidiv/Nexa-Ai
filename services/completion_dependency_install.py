"""Setup 7.25: Dependency Installation Plan.
Plan dependency installation and lockfile validation.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_dependency_install(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['packages', 'manager', 'lockfile']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "dependency_install", **values)

def valid_dependency_install(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "dependency_install" and obj.valid()
