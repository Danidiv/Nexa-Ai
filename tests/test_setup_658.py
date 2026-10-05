from services.completion_learned_pattern_registry import build_learned_pattern_registry, valid_learned_pattern_registry, LearnedPatternRegistry

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.58 TEST")
    print("============================================================")
    obj=build_learned_pattern_registry("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_learned_pattern_registry(obj); print("[PASS] learned pattern registry built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_learned_pattern_registry(obj); print("[PASS] digest validates")
    tampered=LearnedPatternRegistry("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_learned_pattern_registry(tampered); print("[PASS] tamper rejected")
    print("Setup 6.58 tests complete.")

if __name__ == "__main__": main()
