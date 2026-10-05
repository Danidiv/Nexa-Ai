from services.completion_post_patch_validation import build_post_patch_validation, valid_post_patch_validation, PostPatchValidation

def main():
    print("="*60); print("AZIZ AI SETUP 6.94 TEST"); print("="*60)
    obj=build_post_patch_validation('sample', ['compile', 'tests'], ['pass', 'pass'], 'passed')
    assert valid_post_patch_validation(obj); print("[PASS] post-patch validation built")
    assert bool(obj.task_id) and bool(obj.checks) and bool(obj.results) and bool(obj.status); print("[PASS] contract data preserved")
    assert valid_post_patch_validation(obj); print("[PASS] digest validates")
    tampered=PostPatchValidation("tampered", obj.checks, obj.results, obj.status, obj.digest)
    assert not valid_post_patch_validation(tampered); print("[PASS] tamper rejected")
    print("Setup 6.94 tests complete.")

if __name__=="__main__": main()
