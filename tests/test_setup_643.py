from services.completion_acceptance_criteria import build_acceptance_criteria, valid_acceptance_criteria, AcceptanceCriteria

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.43 TEST")
    print("============================================================")
    obj=build_acceptance_criteria("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_acceptance_criteria(obj); print("[PASS] acceptance criteria built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_acceptance_criteria(obj); print("[PASS] digest validates")
    tampered=AcceptanceCriteria("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_acceptance_criteria(tampered); print("[PASS] tamper rejected")
    print("Setup 6.43 tests complete.")

if __name__ == "__main__": main()
