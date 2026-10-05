"""Setup 7.19: Implementation Ordering.
Order multi-layer implementation dependencies safely.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_implementation_order(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['ordered_steps', 'dependencies', 'gates']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "implementation_order", **values)

def valid_implementation_order(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "implementation_order" and obj.valid()
