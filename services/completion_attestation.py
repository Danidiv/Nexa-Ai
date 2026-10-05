"""Setup 4.51: recovery-bound completion attestation and anti-replay protection.

Setup 4.45 sealed the current evidence/verification state. Setup 4.46 additionally
binds a newly-created attestation to the logical task identity so a valid seal from
one conversation/task cannot be replayed for another task or conversation.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any
import json

VERSION = 12
POLICY_IDENTITY_VERSION = 1
EXECUTION_HISTORY_IDENTITY_VERSION = 1
EXECUTION_HISTORY_LIMIT = 64



def _norm(value: Any) -> str:
    return str(value or "").replace("\\", "/").strip()


def _generations_digest(generations: Any) -> str:
    if not isinstance(generations, dict):
        generations = {}
    normalized = {
        _norm(k): max(0, int(v or 0))
        for k, v in generations.items()
        if _norm(k)
    }
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


def _required_digest(paths: Any) -> str:
    values = sorted({_norm(x) for x in (paths or []) if _norm(x)})
    encoded = json.dumps(values, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]



def capability_identity_digest(capabilities: Any) -> str:
    """Return a deterministic digest of the active tool capability surface.

    The capability surface is normalized to tool names plus argument names,
    required flags, and schema types so an attestation cannot be replayed
    against a materially different tool contract.
    """
    if not isinstance(capabilities, (list, tuple)):
        return ""
    normalized = []
    for item in capabilities:
        if not isinstance(item, dict):
            continue
        name = _norm(item.get("name"))
        if not name:
            continue
        args = []
        raw_args = item.get("arguments", [])
        if isinstance(raw_args, (list, tuple)):
            for arg in raw_args:
                if not isinstance(arg, dict):
                    continue
                arg_name = _norm(arg.get("name"))
                if not arg_name:
                    continue
                args.append({
                    "name": arg_name,
                    "required": bool(arg.get("required", False)),
                    "type": _norm(arg.get("type")),
                })
        args.sort(key=lambda value: (value["name"], value["type"], value["required"]))
        normalized.append({"name": name, "arguments": args})
    normalized.sort(key=lambda value: value["name"])
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24] if normalized else ""



def context_identity_digest(context: Any) -> str:
    """Return a deterministic digest for the bounded task execution context.

    The context identity is metadata-only: workspace/project scope, bounded
    paths, and explicit task references are included. Dynamic analysis details
    such as impact graphs and change plans are intentionally excluded so the
    completion seal represents the execution scope rather than transient
    planner output.
    """
    if context is None:
        return ""
    if hasattr(context, "to_dict"):
        try:
            context = context.to_dict()
        except Exception:
            return ""
    if not isinstance(context, dict):
        return ""
    normalized = {
        "workspace_exists": bool(context.get("workspace_exists", False)),
        "project_names": sorted(_norm(x) for x in (context.get("project_names") or []) if _norm(x)),
        "workspace_paths": sorted(_norm(x) for x in (context.get("workspace_paths") or []) if _norm(x)),
        "project_paths": {
            _norm(k): sorted(_norm(x) for x in (v or []) if _norm(x))
            for k, v in (context.get("project_paths") or {}).items()
            if _norm(k)
        },
        "referenced_paths": {
            _norm(k): bool(v)
            for k, v in (context.get("referenced_paths") or {}).items()
            if _norm(k)
        },
    }
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


def runtime_identity_digest(runtime_identity: Any) -> str:
    """Return a deterministic digest for the non-secret execution runtime.

    The identity should contain only safe configuration facts such as backend
    name, model name, and normalized endpoint. Secrets, tokens, request history,
    and transient health state must never be included.
    """
    if isinstance(runtime_identity, dict):
        # Whitelist stable, non-secret identity fields. Transient telemetry and
        # credentials must never affect completion attestation identity.
        normalized = {
            key: _norm(runtime_identity.get(key))
            for key in ("backend", "model", "endpoint")
            if _norm(runtime_identity.get(key))
        }
    else:
        normalized = {"runtime": _norm(runtime_identity)} if _norm(runtime_identity) else {}
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24] if normalized else ""


def build_runtime_identity(gateway: Any = None) -> dict[str, str]:
    """Build a safe runtime identity from the active model gateway."""
    if gateway is None:
        return {}
    base_url = _norm(getattr(gateway, "base_url", ""))
    model = _norm(getattr(gateway, "model", ""))
    backend = gateway.__class__.__name__
    return {
        "backend": backend,
        "model": model,
        "endpoint": base_url,
    }

def task_identity_digest(task_identity: Any) -> str:
    """Return a deterministic short digest for a task-bound identity payload."""
    if isinstance(task_identity, dict):
        normalized = {str(k): _norm(v) for k, v in task_identity.items() if _norm(v)}
    else:
        normalized = {"task": _norm(task_identity)} if _norm(task_identity) else {}
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24] if normalized else ""


def build_task_identity(original_task: Any, conversation_id: Any = "", plan_revision: Any = 0) -> dict[str, str]:
    """Build the stable task identity used by the agent's final completion seal."""
    return {
        "conversation_id": _norm(conversation_id),
        "original_task": _norm(original_task),
        "plan_revision": str(max(0, int(plan_revision or 0))),
    }


def plan_identity_digest(plan: Any) -> str:
    """Return a deterministic digest of the stable execution plan identity.

    The digest binds completion to the actual plan structure, not only its
    revision number. Dynamic current-step state is intentionally excluded.
    """
    if plan is None:
        return ""
    if hasattr(plan, "to_dict"):
        try:
            plan = plan.to_dict()
        except Exception:
            return ""
    if not isinstance(plan, dict):
        return ""
    steps = []
    for step in plan.get("steps", []) or []:
        if not isinstance(step, dict):
            continue
        steps.append({
            "id": _norm(step.get("id")),
            "title": _norm(step.get("title")),
            "objective": _norm(step.get("objective")),
            "dependencies": sorted(_norm(x) for x in (step.get("depends_on") or []) if _norm(x)),
        })
    steps.sort(key=lambda x: x["id"])
    normalized = {
        "task": _norm(plan.get("task")),
        "revision": max(0, int(plan.get("revision", 0) or 0)),
        "steps": steps,
    }
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


def verification_identity_digest(verification: Any) -> str:
    """Return a deterministic digest for the bounded impact-verification state.

    The identity covers required, completed, and missing verification paths plus
    the verification status. Human-facing rationale is intentionally excluded.
    """
    if verification is None:
        return ""
    if hasattr(verification, "to_dict"):
        try:
            verification = verification.to_dict()
        except Exception:
            return ""
    if not isinstance(verification, dict):
        return ""
    def paths(key: str):
        return sorted({_norm(x) for x in (verification.get(key) or []) if _norm(x)})[:64]
    normalized = {
        "status": _norm(verification.get("status")),
        "required_paths": paths("required_paths"),
        "completed_paths": paths("completed_paths"),
        "missing_paths": paths("missing_paths"),
    }
    if not normalized["status"] and not any(normalized[k] for k in ("required_paths", "completed_paths", "missing_paths")):
        return ""
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


def recovery_identity_digest(recovery: Any) -> str:
    """Return a deterministic digest for the bounded evidence-recovery state.

    The identity covers the recovery status, bounded recovery items, and missing
    evidence requirements. Human-facing rationale is intentionally excluded so
    wording changes do not invalidate an otherwise identical recovery state.
    """
    if recovery is None:
        return ""
    if hasattr(recovery, "to_dict"):
        try:
            recovery = recovery.to_dict()
        except Exception:
            return ""
    if not isinstance(recovery, dict):
        return ""
    items = []
    for item in recovery.get("items", []) or []:
        if not isinstance(item, dict):
            continue
        items.append({
            "item_id": _norm(item.get("item_id")),
            "kind": _norm(item.get("kind")),
            "target": _norm(item.get("target")),
            "objective": _norm(item.get("objective")),
            "status": _norm(item.get("status")),
        })
    items.sort(key=lambda x: (x["item_id"], x["kind"], x["target"]))
    normalized = {
        "status": _norm(recovery.get("status")),
        "items": items[:24],
        "missing_evidence": sorted({_norm(x) for x in (recovery.get("missing_evidence") or []) if _norm(x)})[:24],
    }
    if not normalized["status"] and not normalized["items"] and not normalized["missing_evidence"]:
        return ""
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]



def change_plan_identity_digest(change_plan: Any) -> str:
    """Return a deterministic digest for the stable dependency-aware change scope.

    The identity binds completion to targets, inspection scope, change scope,
    verification scope, dependencies, and dependents. Human-facing rationale is
    intentionally excluded because wording changes do not alter the actual scope.
    """
    if change_plan is None:
        return ""
    if hasattr(change_plan, "to_dict"):
        try:
            change_plan = change_plan.to_dict()
        except Exception:
            return ""
    if not isinstance(change_plan, dict):
        return ""

    def paths(key: str):
        return sorted({_norm(x) for x in (change_plan.get(key) or []) if _norm(x)})[:16]

    normalized = {
        "targets": paths("targets"),
        "inspect_paths": paths("inspect_paths"),
        "change_paths": paths("change_paths"),
        "verify_paths": paths("verify_paths"),
        "dependency_paths": paths("dependency_paths"),
        "dependent_paths": paths("dependent_paths"),
    }
    if not any(normalized.values()):
        return ""
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


def execution_history_identity_digest(successful_actions: Any, failed_actions: Any) -> str:
    """Return a deterministic, secret-safe digest of bounded action history.

    Raw action signatures are never stored in the attestation. Only short SHA-256
    fingerprints are included, preserving ordering while keeping arguments/content
    out of the completion seal.
    """
    def fingerprints(values: Any) -> list[str]:
        if not isinstance(values, (list, tuple)):
            return []
        out = []
        for value in list(values)[-EXECUTION_HISTORY_LIMIT:]:
            raw = _norm(value)
            if not raw:
                continue
            out.append(sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:24])
        return out

    normalized = {
        "identity_version": EXECUTION_HISTORY_IDENTITY_VERSION,
        "successful": fingerprints(successful_actions),
        "failed": fingerprints(failed_actions),
    }
    if not normalized["successful"] and not normalized["failed"]:
        return ""
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


def policy_identity_digest(policy: Any) -> str:
    """Return a deterministic digest for the stable agent completion policy.

    Only stable policy facts belong here; runtime telemetry, prompts, evidence
    contents, and transient execution state must not affect this identity.
    """
    if isinstance(policy, dict):
        normalized = {
            str(k): _norm(v) if not isinstance(v, bool) else bool(v)
            for k, v in policy.items()
            if _norm(k)
        }
    else:
        normalized = {"policy": _norm(policy)} if _norm(policy) else {}
    if not normalized:
        return ""
    normalized["identity_version"] = POLICY_IDENTITY_VERSION
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


def build_policy_identity(max_steps: int = 16) -> dict[str, Any]:
    """Build the stable completion policy identity used by the active agent."""
    return {
        "protocol": "OBSERVE-ACT-OBSERVE-VERIFY-REPAIR-VERIFY-DONE",
        "final_answer_requires_attestation": True,
        "read_before_modify": True,
        "read_after_modify": True,
        "tool_evidence_required": True,
        "max_steps": max(0, int(max_steps or 0)),
    }

def answer_identity_digest(answer: Any) -> str:
    """Return a deterministic digest for the final answer bound to a seal.

    Whitespace at the edges is ignored, but internal wording/order remains
    significant. The raw answer is never stored in the attestation.
    """
    value = str(answer or "").strip()
    if not value:
        return ""
    return sha256(value.encode("utf-8", errors="replace")).hexdigest()[:24]


def _seal_payload(attestation: "CompletionAttestation") -> dict[str, Any]:
    return {
        "version": VERSION,
        "checkpoint_hash": str(attestation.checkpoint_hash or ""),
        "checkpoint_sequence": max(0, int(attestation.checkpoint_sequence or 0)),
        "checkpoint_head_hash": str(attestation.checkpoint_head_hash or ""),
        "evidence_status": str(attestation.evidence_status or ""),
        "impact_status": str(attestation.impact_status or ""),
        "change_epoch": max(0, int(attestation.change_epoch or 0)),
        "generations_digest": str(attestation.generations_digest or ""),
        "required_digest": str(attestation.required_digest or ""),
        "task_digest": str(attestation.task_digest or ""),
        "capability_digest": str(attestation.capability_digest or ""),
        "runtime_digest": str(attestation.runtime_digest or ""),
        "context_digest": str(attestation.context_digest or ""),
        "plan_digest": str(attestation.plan_digest or ""),
        "recovery_digest": str(attestation.recovery_digest or ""),
        "verification_digest": str(attestation.verification_digest or ""),
        "policy_digest": str(attestation.policy_digest or ""),
        "execution_history_digest": str(attestation.execution_history_digest or ""),
        "change_plan_digest": str(attestation.change_plan_digest or ""),
        "answer_digest": str(attestation.answer_digest or ""),
        "consumed": bool(attestation.consumed),
    }


def _seal(attestation: "CompletionAttestation") -> str:
    encoded = json.dumps(_seal_payload(attestation), sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8", errors="replace")).hexdigest()[:24]


@dataclass
class CompletionAttestation:
    status: str = "not_required"
    checkpoint_hash: str = ""
    checkpoint_sequence: int = 0
    checkpoint_head_hash: str = ""
    evidence_status: str = "not_required"
    impact_status: str = "not_required"
    change_epoch: int = 0
    generations_digest: str = ""
    required_digest: str = ""
    task_digest: str = ""
    capability_digest: str = ""
    runtime_digest: str = ""
    context_digest: str = ""
    plan_digest: str = ""
    recovery_digest: str = ""
    verification_digest: str = ""
    policy_digest: str = ""
    execution_history_digest: str = ""
    change_plan_digest: str = ""
    answer_digest: str = ""
    consumed: bool = False
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["attestation_version"] = VERSION
        data["checkpoint_sequence"] = max(0, int(self.checkpoint_sequence or 0))
        data["change_epoch"] = max(0, int(self.change_epoch or 0))
        return data

    @classmethod
    def from_dict(cls, data: Any) -> "CompletionAttestation | None":
        if not isinstance(data, dict):
            return None
        version = data.get("attestation_version", 1)
        if version not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, VERSION}:
            return None
        status = str(data.get("status", "not_required"))
        if status not in {"not_required", "sealed"}:
            return None
        return cls(
            status=status,
            checkpoint_hash=str(data.get("checkpoint_hash", "") or ""),
            checkpoint_sequence=max(0, int(data.get("checkpoint_sequence", 0) or 0)),
            checkpoint_head_hash=str(data.get("checkpoint_head_hash", "") or ""),
            evidence_status=str(data.get("evidence_status", "not_required") or "not_required"),
            impact_status=str(data.get("impact_status", "not_required") or "not_required"),
            change_epoch=max(0, int(data.get("change_epoch", 0) or 0)),
            generations_digest=str(data.get("generations_digest", "") or ""),
            required_digest=str(data.get("required_digest", "") or ""),
            task_digest=str(data.get("task_digest", "") or ""),
            capability_digest=str(data.get("capability_digest", "") or ""),
            runtime_digest=str(data.get("runtime_digest", "") or ""),
            context_digest=str(data.get("context_digest", "") or ""),
            plan_digest=str(data.get("plan_digest", "") or ""),
            recovery_digest=str(data.get("recovery_digest", "") or ""),
            verification_digest=str(data.get("verification_digest", "") or ""),
            policy_digest=str(data.get("policy_digest", "") or ""),
            execution_history_digest=str(data.get("execution_history_digest", "") or ""),
            change_plan_digest=str(data.get("change_plan_digest", "") or ""),
            answer_digest=str(data.get("answer_digest", "") or ""),
            consumed=bool(data.get("consumed", False)),
            seal=str(data.get("seal", "") or ""),
        )

    def valid(
        self,
        evidence: Any,
        verification: Any,
        change_epoch: int,
        modified_generations: Any,
        task_identity: Any = None,
        capabilities: Any = None,
        runtime_identity: Any = None,
        task_context: Any = None,
        plan: Any = None,
        recovery: Any = None,
        policy: Any = None,
        successful_actions: Any = None,
        failed_actions: Any = None,
        change_plan: Any = None,
        answer: Any = None,
    ) -> bool:
        if self.status != "sealed" or self.consumed:
            return False
        if evidence is None or verification is None:
            return False
        if getattr(evidence, "status", "") != "sufficient":
            return False
        if getattr(verification, "status", "") != "complete":
            return False
        if not getattr(evidence, "checkpoint_hash", ""):
            return False
        if not evidence.checkpoint_valid():
            return False
        if str(evidence.checkpoint_hash) != self.checkpoint_hash:
            return False
        if max(0, int(evidence.checkpoint_sequence or 0)) != self.checkpoint_sequence:
            return False
        if str(evidence.checkpoint_head_hash or "") != self.checkpoint_head_hash:
            return False
        if max(0, int(change_epoch or 0)) != self.change_epoch:
            return False
        if _generations_digest(modified_generations) != self.generations_digest:
            return False
        required = list(getattr(verification, "required_paths", []) or [])
        if _required_digest(required) != self.required_digest:
            return False
        if str(evidence.status) != self.evidence_status:
            return False
        if str(verification.status) != self.impact_status:
            return False
        # Setup 4.46: new attestations must match the current logical task identity.
        # Version-1 legacy attestations have no task digest and remain restorable,
        # but are not accepted when a task identity is explicitly supplied.
        expected_task_digest = task_identity_digest(task_identity)
        if expected_task_digest:
            if not self.task_digest or self.task_digest != expected_task_digest:
                return False
        elif self.task_digest:
            return False
        # Setup 4.47: attestations are bound to the active tool capability surface.
        expected_capability_digest = capability_identity_digest(capabilities)
        if expected_capability_digest:
            if not self.capability_digest or self.capability_digest != expected_capability_digest:
                return False
        elif self.capability_digest:
            return False
        # Setup 4.48: bind new attestations to the safe execution runtime identity.
        expected_runtime_digest = runtime_identity_digest(runtime_identity)
        if expected_runtime_digest:
            if not self.runtime_digest or self.runtime_digest != expected_runtime_digest:
                return False
        elif self.runtime_digest:
            return False
        # Setup 4.49: bind attestations to the bounded workspace/project
        # execution context so a seal cannot be replayed across scopes.
        expected_context_digest = context_identity_digest(task_context)
        if expected_context_digest:
            if not self.context_digest or self.context_digest != expected_context_digest:
                return False
        elif self.context_digest:
            return False
        # Setup 4.50: bind the seal to the stable plan structure, not merely
        # the plan revision, so modified objectives/dependencies cannot reuse it.
        expected_plan_digest = plan_identity_digest(plan)
        if expected_plan_digest:
            if not self.plan_digest or self.plan_digest != expected_plan_digest:
                return False
        elif self.plan_digest:
            return False
        # Setup 4.52: bind completion to the bounded impact-verification state
        # so completed/missing verification paths cannot be silently changed.
        expected_verification_digest = verification_identity_digest(verification)
        if expected_verification_digest:
            if not self.verification_digest or self.verification_digest != expected_verification_digest:
                return False
        elif self.verification_digest:
            return False
        # Setup 4.51: bind completion to the bounded evidence-recovery state.
        expected_recovery_digest = recovery_identity_digest(recovery)
        if expected_recovery_digest:
            if not self.recovery_digest or self.recovery_digest != expected_recovery_digest:
                return False
        elif self.recovery_digest:
            return False
        # Setup 4.53: bind completion to the stable agent completion policy.
        expected_policy_digest = policy_identity_digest(policy)
        if expected_policy_digest:
            if not self.policy_digest or self.policy_digest != expected_policy_digest:
                return False
        elif self.policy_digest:
            return False
        # Setup 4.54: bind completion to the bounded execution history.
        # This uses fingerprints only, so raw tool arguments/results never enter
        # the attestation while action ordering remains replay-sensitive.
        expected_execution_history_digest = execution_history_identity_digest(
            successful_actions, failed_actions
        )
        if expected_execution_history_digest:
            if not self.execution_history_digest or self.execution_history_digest != expected_execution_history_digest:
                return False
        elif self.execution_history_digest:
            return False
        # Setup 4.55: bind completion to the stable dependency-aware change scope.
        expected_change_plan_digest = change_plan_identity_digest(change_plan)
        if expected_change_plan_digest:
            if not self.change_plan_digest or self.change_plan_digest != expected_change_plan_digest:
                return False
        elif self.change_plan_digest:
            return False
        # Setup 4.56: bind a new completion seal to the exact final answer.
        # This prevents a valid completion receipt from being replayed with a
        # materially different completion message. Legacy attestations without
        # an answer digest remain restorable, but cannot be accepted when an
        # explicit answer is supplied.
        expected_answer_digest = answer_identity_digest(answer)
        if expected_answer_digest:
            if not self.answer_digest or self.answer_digest != expected_answer_digest:
                return False
        elif self.answer_digest:
            return False
        return _seal(self) == self.seal

    def consume(self) -> bool:
        """Consume this completion attestation exactly once.

        Consumption is persisted in the attestation seal. A consumed attestation
        can never validate again, preventing replay after completion/restart.
        """
        if self.status != "sealed" or self.consumed:
            return False
        self.consumed = True
        self.seal = _seal(self)
        return True


def create_attestation(
    evidence: Any,
    verification: Any,
    change_epoch: int,
    modified_generations: Any,
    task_identity: Any = None,
    capabilities: Any = None,
    runtime_identity: Any = None,
    task_context: Any = None,
    plan: Any = None,
    recovery: Any = None,
    policy: Any = None,
    successful_actions: Any = None,
    failed_actions: Any = None,
    change_plan: Any = None,
    answer: Any = None,
) -> CompletionAttestation:
    """Create a completion seal only when all completion prerequisites are satisfied."""
    if evidence is None or verification is None:
        return CompletionAttestation()
    if getattr(evidence, "status", "") != "sufficient" or getattr(verification, "status", "") != "complete":
        return CompletionAttestation()
    if not evidence.checkpoint_hash:
        evidence.create_checkpoint()
    attestation = CompletionAttestation(
        status="sealed",
        checkpoint_hash=str(evidence.checkpoint_hash or ""),
        checkpoint_sequence=max(0, int(evidence.checkpoint_sequence or 0)),
        checkpoint_head_hash=str(evidence.checkpoint_head_hash or ""),
        evidence_status=str(evidence.status),
        impact_status=str(verification.status),
        change_epoch=max(0, int(change_epoch or 0)),
        generations_digest=_generations_digest(modified_generations),
        required_digest=_required_digest(getattr(verification, "required_paths", []) or []),
        task_digest=task_identity_digest(task_identity),
        capability_digest=capability_identity_digest(capabilities),
        runtime_digest=runtime_identity_digest(runtime_identity),
        context_digest=context_identity_digest(task_context),
        plan_digest=plan_identity_digest(plan),
        recovery_digest=recovery_identity_digest(recovery),
        verification_digest=verification_identity_digest(verification),
        policy_digest=policy_identity_digest(policy),
        execution_history_digest=execution_history_identity_digest(successful_actions, failed_actions),
        change_plan_digest=change_plan_identity_digest(change_plan),
        answer_digest=answer_identity_digest(answer),
    )
    attestation.seal = _seal(attestation)
    return attestation
