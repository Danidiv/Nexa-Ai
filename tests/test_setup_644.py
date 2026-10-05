from services.completion_change_scope_inference import build_change_scope_inference, valid_change_scope_inference, ChangeScopeInference

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.44 TEST")
    print("============================================================")
    obj=build_change_scope_inference("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_change_scope_inference(obj); print("[PASS] change scope inference built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_change_scope_inference(obj); print("[PASS] digest validates")
    tampered=ChangeScopeInference("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_change_scope_inference(tampered); print("[PASS] tamper rejected")
    print("Setup 6.44 tests complete.")

if __name__ == "__main__": main()
