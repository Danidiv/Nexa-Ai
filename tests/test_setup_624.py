from services.completion_multifile_patch_plan import build_multifile_patch_plan, valid_multifile_patch_plan, MultiFilePatchPlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.24 TEST")
    print("============================================================")
    obj=build_multifile_patch_plan(["a","b"], ["a","b"], ["a","b"], ["a","b"])
    assert valid_multifile_patch_plan(obj); print("[PASS] multi-file patch plan built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_multifile_patch_plan(obj); print("[PASS] digest validates")
    assert not valid_multifile_patch_plan(MultiFilePatchPlan(( "tampered", ), obj.operations, obj.order, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.24 tests complete.")
if __name__ == "__main__": main()
