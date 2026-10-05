"""Setup 7.44: Product Quality Score.
Score product readiness from verified evidence.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_quality_score(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['functional', 'visual', 'runtime', 'security']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "quality_score", **values)

def valid_quality_score(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "quality_score" and obj.valid()
