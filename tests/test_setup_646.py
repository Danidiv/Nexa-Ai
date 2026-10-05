from services.completion_edit_ordering import build_edit_ordering, valid_edit_ordering, EditOrdering

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.46 TEST")
    print("============================================================")
    obj=build_edit_ordering("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_edit_ordering(obj); print("[PASS] edit ordering built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_edit_ordering(obj); print("[PASS] digest validates")
    tampered=EditOrdering("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_edit_ordering(tampered); print("[PASS] tamper rejected")
    print("Setup 6.46 tests complete.")

if __name__ == "__main__": main()
