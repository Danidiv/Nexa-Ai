from services.completion_repository_state_snapshot import build_repository_state_snapshot, valid_repository_state_snapshot, RepositoryStateSnapshot

def main():
    print("="*60); print("AZIZ AI SETUP 6.82 TEST"); print("="*60)
    obj=build_repository_state_snapshot('sample', ['app.py'], ['requests'], ['test_app.py'])
    assert valid_repository_state_snapshot(obj); print("[PASS] repository state snapshot built")
    assert bool(obj.task_id) and bool(obj.files) and bool(obj.dependencies) and bool(obj.tests); print("[PASS] contract data preserved")
    assert valid_repository_state_snapshot(obj); print("[PASS] digest validates")
    tampered=RepositoryStateSnapshot("tampered", obj.files, obj.dependencies, obj.tests, obj.digest)
    assert not valid_repository_state_snapshot(tampered); print("[PASS] tamper rejected")
    print("Setup 6.82 tests complete.")

if __name__=="__main__": main()
