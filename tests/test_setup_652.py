from services.completion_patch_validation import build_patch_validation, valid_patch_validation, PatchValidation

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.52 TEST")
    print("============================================================")
    obj=build_patch_validation("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_patch_validation(obj); print("[PASS] patch validation built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_patch_validation(obj); print("[PASS] digest validates")
    tampered=PatchValidation("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_patch_validation(tampered); print("[PASS] tamper rejected")
    print("Setup 6.52 tests complete.")

if __name__ == "__main__": main()
