"""Setup 7.06: UI Structure Mapping.
Represent pages, components, and navigation relationships.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_ui_structure(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['pages', 'components', 'routes']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "ui_structure", **values)

def valid_ui_structure(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "ui_structure" and obj.valid()
