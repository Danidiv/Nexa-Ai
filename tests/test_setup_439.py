"""Setup 4.39 tests: freshness-bound completion evidence."""
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.evidence_freshness import next_change_epoch, normalize_epoch, is_fresh
from services.impact_verification import build_impact_verification
from core.agent.agent_loop import AgentState, _safe_state_snapshot, _restore_state_snapshot


def plan():
    return {"verify_paths": ["app.js", "index.html"], "targets": ["app.js"], "dependent_paths": ["index.html"]}


def ready_ledger(epoch=1):
    verification = build_impact_verification(plan(), {"app.js"}, {"app.js", "index.html"})
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS", epoch))
    ledger.add(make_evidence("read_file", "verification", "app.js", "SUCCESS", epoch))
    ledger.add(make_evidence("read_file", "verification", "index.html", "SUCCESS", epoch))
    ledger.evaluate(verification, True, epoch)
    return ledger, verification


def test_stale_evidence_cannot_complete_new_change():
    ledger, verification = ready_ledger(1)
    ledger.evaluate(verification, True, 2)
    assert ledger.status == "insufficient"
    assert "successful modification evidence" in ledger.missing_requirements
    print("[PASS] stale evidence cannot complete a newer change epoch")


def test_current_epoch_evidence_completes():
    ledger, verification = ready_ledger(3)
    assert ledger.status == "sufficient"
    assert ledger.missing_requirements == []
    print("[PASS] current-epoch modification and verification evidence is sufficient")


def test_new_modification_requires_fresh_verification():
    verification = build_impact_verification(plan(), {"app.js"}, {"app.js", "index.html"})
    ledger, _ = ready_ledger(1)
    ledger.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS-2", 2))
    ledger.evaluate(verification, True, 2)
    assert ledger.status == "insufficient"
    assert any("verification evidence for" in item for item in ledger.missing_requirements)
    print("[PASS] a new modification invalidates prior verification evidence")


def test_epoch_helpers_are_bounded_and_deterministic():
    assert normalize_epoch(-5) == 0
    assert next_change_epoch(0) == 1
    assert next_change_epoch(7) == 8
    assert is_fresh({"change_epoch": 8}, 8)
    assert not is_fresh({"change_epoch": 7}, 8)
    print("[PASS] evidence freshness helpers are bounded and deterministic")


def test_legacy_evidence_restores_as_epoch_zero():
    legacy = {
        "evidence_version": 1,
        "entries": [{
            "evidence_version": 1,
            "evidence_id": "x",
            "action": "read_file",
            "category": "verification",
            "path": "app.js",
            "outcome": "success",
            "fingerprint": "abc",
        }],
        "status": "insufficient",
        "missing_requirements": [],
    }
    restored = CompletionEvidenceLedger.from_dict(legacy)
    assert restored is not None
    assert restored.entries[0]["change_epoch"] == 0
    print("[PASS] legacy evidence restores safely with epoch zero")


def test_change_epoch_persists_in_agent_state():
    state = AgentState()
    state.change_epoch = 4
    snapshot = _safe_state_snapshot(state)
    assert snapshot["change_epoch"] == 4
    restored = AgentState()
    _restore_state_snapshot(restored, snapshot)
    assert restored.change_epoch == 4
    print("[PASS] change epoch persists and restores through agent state")


def test_informational_state_remains_unaffected():
    state = AgentState()
    assert state.change_epoch == 0
    state.completion_evidence.evaluate(None, False, state.change_epoch)
    assert state.completion_evidence.status == "not_required"
    print("[PASS] informational/non-modifying tasks remain outside freshness gating")


if __name__ == "__main__":
    print("=" * 60)
    print("AZIZ AI SETUP 4.39 TEST")
    print("=" * 60)
    for name in (
        "test_stale_evidence_cannot_complete_new_change",
        "test_current_epoch_evidence_completes",
        "test_new_modification_requires_fresh_verification",
        "test_epoch_helpers_are_bounded_and_deterministic",
        "test_legacy_evidence_restores_as_epoch_zero",
        "test_change_epoch_persists_in_agent_state",
        "test_informational_state_remains_unaffected",
    ):
        globals()[name]()
    print("\nSetup 4.39 tests complete.")
