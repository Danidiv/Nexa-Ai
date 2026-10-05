"""Setup 7.22: Tool Selection.
Select the safest available tool for each execution step.
"""
from __future__ import annotations
from .product_builder_primitives import ProductArtifact, artifact

def build_tool_selection(task_id: str, **kwargs) -> ProductArtifact:
    values={}
    for field in ['step_tools', 'read_before_write', 'verification']:
        value=kwargs.get(field, [])
        if isinstance(value, list): value=tuple(value)
        values[field]=value
    return artifact(task_id, "tool_selection", **values)

def valid_tool_selection(obj: ProductArtifact) -> bool:
    return isinstance(obj, ProductArtifact) and obj.kind == "tool_selection" and obj.valid()
