from services.completion_failure_evidence_normalization import build_failure_evidence_normalization, valid_failure_evidence_normalization, FailureEvidenceNormalization

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.49 TEST")
    print("============================================================")
    obj=build_failure_evidence_normalization("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_failure_evidence_normalization(obj); print("[PASS] failure evidence normalization built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_failure_evidence_normalization(obj); print("[PASS] digest validates")
    tampered=FailureEvidenceNormalization("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_failure_evidence_normalization(tampered); print("[PASS] tamper rejected")
    print("Setup 6.49 tests complete.")

if __name__ == "__main__": main()
