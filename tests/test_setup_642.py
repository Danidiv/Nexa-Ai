from services.completion_requirement_normalization import build_requirement_normalization, valid_requirement_normalization, RequirementNormalization

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.42 TEST")
    print("============================================================")
    obj=build_requirement_normalization("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_requirement_normalization(obj); print("[PASS] requirement normalization built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_requirement_normalization(obj); print("[PASS] digest validates")
    tampered=RequirementNormalization("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_requirement_normalization(tampered); print("[PASS] tamper rejected")
    print("Setup 6.42 tests complete.")

if __name__ == "__main__": main()
