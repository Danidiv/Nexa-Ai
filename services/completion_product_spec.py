"""Setup 7.51: deterministic product requirement specification."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from .product_builder_primitives import digest, require_text, bounded

@dataclass(frozen=True)
class ProductSpec:
    task_id: str
    goal: str
    features: tuple[str, ...]
    constraints: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    digest_value: str = ""

    def sealed(self) -> "ProductSpec":
        data = {
            "task_id": self.task_id,
            "goal": self.goal,
            "features": list(self.features),
            "constraints": list(self.constraints),
            "acceptance_criteria": list(self.acceptance_criteria),
        }
        return ProductSpec(self.task_id, self.goal, self.features,
                           self.constraints, self.acceptance_criteria, digest(data))

    def valid(self) -> bool:
        data = {
            "task_id": self.task_id,
            "goal": self.goal,
            "features": list(self.features),
            "constraints": list(self.constraints),
            "acceptance_criteria": list(self.acceptance_criteria),
        }
        return bool(self.digest_value) and self.digest_value == digest(data)

    def to_dict(self):
        return asdict(self)


def _normalize(values, name: str) -> tuple[str, ...]:
    values = bounded(values, name)
    result = []
    for value in values:
        result.append(require_text(value, name))
    return tuple(result)


def build_product_spec(
    task_id: str,
    goal: str,
    features=(),
    constraints=(),
    acceptance_criteria=(),
) -> ProductSpec:
    task_id = require_text(task_id, "task_id")
    goal = require_text(goal, "goal")
    return ProductSpec(
        task_id,
        goal,
        _normalize(features, "features"),
        _normalize(constraints, "constraints"),
        _normalize(acceptance_criteria, "acceptance_criteria"),
        "",
    ).sealed()


def valid_product_spec(obj: ProductSpec) -> bool:
    return isinstance(obj, ProductSpec) and obj.valid()
