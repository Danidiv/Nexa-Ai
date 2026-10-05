"""Setup 4.49 task-context-bound completion attestation tests."""
from services.completion_attestation import (
    CompletionAttestation,
    build_task_identity,
    context_identity_digest,
    create_attestation,
)
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.impact_verification import ImpactVerification
from services.task_context import TaskContext

CAPS = [{"name": "write_file", "arguments": [{"name": "path", "required": True, "type": "string"}]}]
RUNTIME = {"backend": "LMStudioGateway", "model": "qwen/qwen3.5-9b", "endpoint": "http://localhost:1234/v1"}
CONTEXT = TaskContext(
    True,
    ["demo"],
    ["app/a.py"],
    {"demo": ["src/main.py", "README.md"]},
    {"app/a.py": True},
)


def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file", "modification", "app/a.py", {"ok": True}, 1, 1))
    ledger.add(make_evidence("read_file", "verification", "app/a.py", {"ok": True}, 1, 1))
    verification = ImpactVerification(["app/a.py"], ["app/a.py"], [], "complete", "verified")
    ledger.evaluate(verification, True, 1, {"app/a.py": 1})
    return ledger, verification


def _identity():
    return build_task_identity("edit app/a.py", "conv-1", 2)


def _att():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS, RUNTIME, CONTEXT)
    return ledger, verification, att


def test_context_bound_attestation_validates():
    ledger, verification, att = _att()
    assert att.status == "sealed"
    assert att.context_digest == context_identity_digest(CONTEXT)
    assert att.valid(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS, RUNTIME, CONTEXT)


def test_changed_project_context_invalidates_attestation():
    ledger, verification, att = _att()
    changed = TaskContext(True, ["demo", "other"], CONTEXT.workspace_paths, CONTEXT.project_paths, CONTEXT.referenced_paths)
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS, RUNTIME, changed)


def test_context_digest_is_deterministic_and_ignores_dynamic_planner_details():
    a = TaskContext(True, ["demo"], ["app/a.py"], {"demo": ["src/main.py"]}, {"app/a.py": True}, {"graph": 1}, {"targets": ["app/a.py"]})
    b = TaskContext(True, ["demo"], ["app/a.py"], {"demo": ["src/main.py"]}, {"app/a.py": True}, {"graph": 999}, {"targets": ["other.py"]})
    assert context_identity_digest(a) == context_identity_digest(b)
    assert len(context_identity_digest(a)) == 24


def test_legacy_setup_448_attestation_restores_without_context_binding():
    restored = CompletionAttestation.from_dict({"attestation_version": 4, "status": "not_required"})
    assert restored is not None
    assert restored.context_digest == ""
    assert not restored.valid(None, None, 0, {}, _identity(), CAPS, RUNTIME, CONTEXT)


def test_missing_context_identity_cannot_reuse_new_attestation():
    ledger, verification, att = _att()
    assert not att.valid(ledger, verification, 1, {"app/a.py": 1}, _identity(), CAPS, RUNTIME, None)


def test_context_digest_changes_when_referenced_path_state_changes():
    present = TaskContext(True, ["demo"], ["app/a.py"], {"demo": ["src/main.py"]}, {"app/a.py": True})
    missing = TaskContext(True, ["demo"], ["app/a.py"], {"demo": ["src/main.py"]}, {"app/a.py": False})
    assert context_identity_digest(present) != context_identity_digest(missing)


def main():
    tests = [
        ("context-bound attestation validates", test_context_bound_attestation_validates),
        ("changed project context invalidates attestation", test_changed_project_context_invalidates_attestation),
        ("context digest is deterministic and ignores dynamic planner details", test_context_digest_is_deterministic_and_ignores_dynamic_planner_details),
        ("legacy Setup 4.48 attestation restores without context binding", test_legacy_setup_448_attestation_restores_without_context_binding),
        ("missing context identity cannot reuse new attestation", test_missing_context_identity_cannot_reuse_new_attestation),
        ("context digest changes when referenced path state changes", test_context_digest_changes_when_referenced_path_state_changes),
    ]
    print("=" * 60)
    print("AZIZ AI SETUP 4.49 TEST")
    print("=" * 60)
    for name, test in tests:
        try:
            test()
            print(f"[PASS] {name}")
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            raise SystemExit(1)
    print("\nSetup 4.49 tests complete.")


if __name__ == "__main__":
    main()
