"""Setup 4.70 tests: deterministic terminal emission recovery resolution."""
from __future__ import annotations

from services.completion_emission_resolution import CompletionEmissionResolution, issue_resolution


class Recovery:
    def __init__(self, status="reconciled", valid=True):
        self.status = status
        self.recovery_id = "recovery-1"
        self.emission_id = "emission-1"
        self.audit_id = "audit-1"
        self.conversation_id_digest = "conv-digest"
        self.task_digest = "task-1"
        self.answer_digest = "answer-1"
        self.change_epoch = 7
        self._valid = valid
    def valid(self):
        return self._valid


def test_reconciled_is_ready():
    r = issue_resolution(Recovery())
    assert r.status == "ready" and r.decision == "finalize"
    assert r.valid() and not r.blocks_finalization()


def test_pending_requires_verification():
    r = issue_resolution(Recovery("pending"))
    assert r.status == "resume_verification"
    assert r.blocks_finalization() and not r.requires_fresh_completion()


def test_orphaned_is_quarantined():
    r = issue_resolution(Recovery("orphaned"))
    assert r.status == "quarantine" and r.decision == "quarantine"
    assert r.blocks_finalization() and r.requires_fresh_completion()


def test_invalid_recovery_is_blocked():
    r = issue_resolution(Recovery("reconciled", valid=False))
    assert r.status == "invalid" and r.reason_code == "recovery_invalid"
    assert r.blocks_finalization() and r.requires_fresh_completion()


def test_unknown_status_is_invalid():
    r = issue_resolution(Recovery("unexpected"))
    assert r.status == "invalid"
    assert r.valid()


def test_context_binding_is_preserved():
    r = issue_resolution(Recovery(), "conv-1", "task-2", "answer-2", 9)
    assert not r.matches_context("other", "task-2", "answer-2", 9)
    assert r.matches_context("conv-1", "task-2", "answer-2", 9)


def test_tamper_is_rejected():
    r = issue_resolution(Recovery())
    r.reason_code = "tampered"
    assert not r.valid()


def test_serialization_and_legacy_restore():
    r = issue_resolution(Recovery())
    restored = CompletionEmissionResolution.from_dict(r.to_dict())
    assert restored is not None and restored.valid()
    legacy = r.to_dict(); legacy.pop("completion_emission_resolution_version", None)
    restored_legacy = CompletionEmissionResolution.from_dict(legacy)
    assert restored_legacy is not None and restored_legacy.valid()


def test_not_required_is_empty():
    r = issue_resolution(None)
    assert r.status == "not_required" and r.valid()


def test_resolution_is_read_only():
    rec = Recovery("orphaned")
    before = rec.__dict__.copy()
    issue_resolution(rec)
    assert rec.__dict__ == before


def main():
    tests = [
        ("reconciled recovery is ready", test_reconciled_is_ready),
        ("pending recovery requires verification", test_pending_requires_verification),
        ("orphaned recovery is quarantined", test_orphaned_is_quarantined),
        ("invalid recovery is blocked", test_invalid_recovery_is_blocked),
        ("unknown recovery status is invalid", test_unknown_status_is_invalid),
        ("context binding is preserved", test_context_binding_is_preserved),
        ("tampered resolution is rejected", test_tamper_is_rejected),
        ("serialization and legacy restore", test_serialization_and_legacy_restore),
        ("no recovery is not required", test_not_required_is_empty),
        ("resolution is read-only", test_resolution_is_read_only),
    ]
    print("=" * 60); print("AZIZ AI SETUP 4.70 TEST"); print("=" * 60)
    for name, fn in tests:
        fn(); print(f"[PASS] {name}")
    print("\nSetup 4.70 tests complete.")

if __name__ == "__main__":
    main()
