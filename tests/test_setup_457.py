"""Setup 4.57 one-time completion attestation consumption tests."""
from services.completion_attestation import (
    CompletionAttestation, build_policy_identity, build_task_identity, create_attestation,
)
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.evidence_recovery import EvidenceRecoveryPlan
from services.impact_verification import ImpactVerification
from services.task_planner import TaskPlan, PlanStep
from services.change_planner import ChangePlan

CAPS = [{"name":"write_file","arguments":[{"name":"path","required":True,"type":"string"}]}]
RUNTIME = {"backend":"LMStudioGateway","model":"qwen/qwen3.5-9b","endpoint":"http://localhost:1234/v1"}
IDENTITY = build_task_identity("edit app/a.py", "conv-1", 2)
PLAN = TaskPlan("edit app/a.py", [PlanStep("S1","Inspect","Inspect app/a.py",[]), PlanStep("S2","Edit","Edit app/a.py",["S1"])])
RECOVERY = EvidenceRecoveryPlan("complete", [], [], ["Completion evidence is already sufficient."])
POLICY = build_policy_identity(16)
CHANGE_PLAN = ChangePlan(targets=["app/a.py"], inspect_paths=["lib/base.py","app/a.py"], change_paths=["app/a.py"], verify_paths=["app/a.py","app/main.py"], dependency_paths=["lib/base.py"], dependent_paths=["app/main.py"], rationale=["stable rationale"])
SUCCESS = ["write_file|{\"path\":\"app/a.py\"}", "read_file|{\"path\":\"app/a.py\"}"]
FAILED = ["run_command|{\"command\":\"bad\"}"]
ANSWER = "Updated app/a.py and verified the affected resources successfully."

def _ready():
    ledger = CompletionEvidenceLedger([], "not_required", [])
    ledger.add(make_evidence("write_file","modification","app/a.py",{"ok":True},1,1))
    ledger.add(make_evidence("read_file","verification","app/a.py",{"ok":True},1,1))
    verification = ImpactVerification(["app/a.py"],["app/a.py"],[],"complete","verified")
    ledger.evaluate(verification, True, 1, {"app/a.py":1})
    return ledger, verification

def _att():
    ledger, verification = _ready()
    att = create_attestation(ledger, verification, 1, {"app/a.py":1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY, POLICY, SUCCESS, FAILED, CHANGE_PLAN, ANSWER)
    return ledger, verification, att

def _valid(att, ledger, verification):
    return att.valid(ledger, verification, 1, {"app/a.py":1}, IDENTITY, CAPS, RUNTIME, None, PLAN, RECOVERY, POLICY, SUCCESS, FAILED, CHANGE_PLAN, ANSWER)

def test_one_time_consumption_succeeds():
    ledger, verification, att = _att()
    assert _valid(att, ledger, verification)
    assert att.consume()
    assert att.consumed is True

def test_consumed_attestation_cannot_be_reused():
    ledger, verification, att = _att(); assert att.consume(); assert not _valid(att, ledger, verification)

def test_consumption_survives_state_serialization():
    ledger, verification, att = _att(); assert att.consume(); restored = CompletionAttestation.from_dict(att.to_dict()); assert restored is not None and restored.consumed is True; assert not _valid(restored, ledger, verification)

def test_replay_attempt_is_rejected():
    _, _, att = _att(); assert att.consume(); assert not att.consume()

def test_legacy_setup_456_restores_safely():
    restored = CompletionAttestation.from_dict({"attestation_version":11,"status":"sealed","answer_digest":"abc","seal":"legacy"}); assert restored is not None and restored.consumed is False

def test_new_attestation_remains_consumable_after_legacy_restore():
    ledger, verification, att = _att(); raw=att.to_dict(); raw["attestation_version"]=11; raw.pop("consumed",None); restored=CompletionAttestation.from_dict(raw); assert restored is not None and restored.consumed is False; assert restored.consume()

def main():
    tests=[("one-time attestation consumption succeeds",test_one_time_consumption_succeeds),("consumed attestation cannot be reused",test_consumed_attestation_cannot_be_reused),("consumption survives state serialization",test_consumption_survives_state_serialization),("replay attempt is rejected",test_replay_attempt_is_rejected),("legacy Setup 4.56 attestation restores safely",test_legacy_setup_456_restores_safely),("new attestation remains consumable after legacy restore",test_new_attestation_remains_consumable_after_legacy_restore)]
    print("="*60); print("AZIZ AI SETUP 4.57 TEST"); print("="*60)
    for name,test in tests:
        try: test(); print(f"[PASS] {name}")
        except Exception as exc: print(f"[FAIL] {name}: {exc}"); raise SystemExit(1)
    print("\nSetup 4.57 tests complete.")
if __name__ == "__main__": main()
