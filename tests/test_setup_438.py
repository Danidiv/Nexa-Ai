"""Setup 4.38 tests: evidence-based repair and recovery."""
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.evidence_recovery import build_evidence_recovery, EvidenceRecoveryPlan
from services.impact_verification import build_impact_verification
from core.agent.agent_loop import AgentState, _safe_state_snapshot, _restore_state_snapshot


def plan():
    return {"verify_paths": ["app.js", "index.html"], "targets": ["app.js"], "dependent_paths": ["index.html"]}


def test_missing_verification_creates_targeted_recovery():
    verification = build_impact_verification(plan(), {"app.js"}, set())
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS"))
    ledger.add(make_evidence("read_file", "verification", "app.js", "SUCCESS"))
    ledger.evaluate(verification, True)
    recovery = build_evidence_recovery(ledger, verification, True)
    assert recovery.status == "pending"
    assert any(item["target"] == "index.html" for item in recovery.items)
    print("[PASS] missing verification evidence creates a targeted recovery checkpoint")


def test_recovery_does_not_invent_unrequired_paths():
    verification = build_impact_verification({"verify_paths": ["app.js"]}, {"app.js"}, set())
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS"))
    ledger.evaluate(verification, True)
    recovery = build_evidence_recovery(ledger, verification, True)
    assert [x["target"] for x in recovery.items] == ["app.js"]
    print("[PASS] recovery remains scoped to explicitly required verification paths")


def test_recovery_marks_complete_when_evidence_is_sufficient():
    verification = build_impact_verification(plan(), {"app.js"}, {"app.js", "index.html"})
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS"))
    ledger.add(make_evidence("read_file", "verification", "app.js", "SUCCESS"))
    ledger.add(make_evidence("read_file", "verification", "index.html", "SUCCESS"))
    ledger.evaluate(verification, True)
    recovery = build_evidence_recovery(ledger, verification, True)
    assert recovery.status == "complete"
    assert recovery.items == []
    print("[PASS] recovery closes when completion evidence becomes sufficient")


def test_recovery_items_are_deduplicated_and_bounded():
    verification = build_impact_verification({"verify_paths": [f"f{i}.js" for i in range(40)]}, {"f0.js"}, set())
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "f0.js", "SUCCESS"))
    ledger.evaluate(verification, True)
    recovery = build_evidence_recovery(ledger, verification, True)
    assert len(recovery.items) <= 24
    assert len({x["item_id"] for x in recovery.items}) == len(recovery.items)
    print("[PASS] recovery remains deduplicated and bounded")


def test_recovery_is_json_safe_and_restores():
    verification = build_impact_verification(plan(), {"app.js"}, {"app.js"})
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS"))
    ledger.evaluate(verification, True)
    recovery = build_evidence_recovery(ledger, verification, True)
    restored = EvidenceRecoveryPlan.from_dict(recovery.to_dict())
    assert restored is not None
    assert restored.to_dict() == recovery.to_dict()
    print("[PASS] recovery plan serializes and restores as JSON-safe state")


def test_recovery_next_item_is_deterministic():
    verification = build_impact_verification(plan(), {"app.js"}, set())
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS"))
    ledger.evaluate(verification, True)
    recovery = build_evidence_recovery(ledger, verification, True)
    first = recovery.next_item()
    assert first is not None
    recovery.mark_target_complete(first["target"])
    assert recovery.next_item() is not None
    assert recovery.next_item()["target"] == "index.html"
    print("[PASS] recovery advances through deterministic targeted checkpoints")


def test_agent_state_persists_recovery_checkpoint():
    state = AgentState()
    state.verification_requested = True
    state.modified_resources = {"app.js"}
    state.observed_resources = {"app.js"}
    state.impact_verification = build_impact_verification(plan(), state.modified_resources, state.observed_resources)
    state.completion_evidence.add(make_evidence("edit_file", "modification", "app.js", "SUCCESS"))
    state.completion_evidence.add(make_evidence("read_file", "verification", "app.js", "SUCCESS"))
    state.completion_evidence.evaluate(state.impact_verification, True)
    state.evidence_recovery = build_evidence_recovery(state.completion_evidence, state.impact_verification, True)
    snapshot = _safe_state_snapshot(state)
    restored = AgentState()
    _restore_state_snapshot(restored, snapshot)
    assert restored.evidence_recovery is not None
    assert restored.evidence_recovery.status == "pending"
    assert restored.evidence_recovery.next_item()["target"] == "index.html"
    print("[PASS] agent state restores the evidence recovery checkpoint safely")


if __name__ == "__main__":
    print("=" * 60)
    print("AZIZ AI SETUP 4.38 TEST")
    print("=" * 60)
    for name in (
        "test_missing_verification_creates_targeted_recovery",
        "test_recovery_does_not_invent_unrequired_paths",
        "test_recovery_marks_complete_when_evidence_is_sufficient",
        "test_recovery_items_are_deduplicated_and_bounded",
        "test_recovery_is_json_safe_and_restores",
        "test_recovery_next_item_is_deterministic",
        "test_agent_state_persists_recovery_checkpoint",
    ):
        globals()[name]()
    print("\nSetup 4.38 tests complete.")
