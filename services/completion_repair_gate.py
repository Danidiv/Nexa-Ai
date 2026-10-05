"""Setup 7.42: Repair Safety Gate.
Gate repairs using scope, risk, and verification requirements.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_repair_gate(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['risk', 'scope', 'required_evidence']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "repair_gate", **values)

def valid_repair_gate(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "repair_gate" and obj.valid()
