"""Setup 7.08: Data Model Mapping.
Represent entities and relationships needed by the product.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_data_model(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['entities', 'relations', 'constraints']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "data_model", **values)

def valid_data_model(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "data_model" and obj.valid()
