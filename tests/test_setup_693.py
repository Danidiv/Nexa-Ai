from services.completion_patch_application import build_patch_application, valid_patch_application, PatchApplication

def main():
    print("="*60); print("AZIZ AI SETUP 6.93 TEST"); print("="*60)
    obj=build_patch_application('sample', ['app.py'], ['replace return'], ['applied'])
    assert valid_patch_application(obj); print("[PASS] patch application built")
    assert bool(obj.task_id) and bool(obj.files) and bool(obj.operations) and bool(obj.result); print("[PASS] contract data preserved")
    assert valid_patch_application(obj); print("[PASS] digest validates")
    tampered=PatchApplication("tampered", obj.files, obj.operations, obj.result, obj.digest)
    assert not valid_patch_application(tampered); print("[PASS] tamper rejected")
    print("Setup 6.93 tests complete.")

if __name__=="__main__": main()
