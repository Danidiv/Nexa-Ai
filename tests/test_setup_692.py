from services.completion_patch_safety import build_patch_safety, valid_patch_safety, PatchSafety

def main():
    print("="*60); print("AZIZ AI SETUP 6.92 TEST"); print("="*60)
    obj=build_patch_safety('sample', ['app.py'], ['syntax', 'scope'], ['low'])
    assert valid_patch_safety(obj); print("[PASS] patch safety built")
    assert bool(obj.task_id) and bool(obj.files) and bool(obj.checks) and bool(obj.risk); print("[PASS] contract data preserved")
    assert valid_patch_safety(obj); print("[PASS] digest validates")
    tampered=PatchSafety("tampered", obj.files, obj.checks, obj.risk, obj.digest)
    assert not valid_patch_safety(tampered); print("[PASS] tamper rejected")
    print("Setup 6.92 tests complete.")

if __name__=="__main__": main()
