from services.completion_runtime_verification import build_runtime_verification, valid_runtime_verification, RuntimeVerification

def main():
    print("="*60); print("AZIZ AI SETUP 6.96 TEST"); print("="*60)
    obj=build_runtime_verification('sample', 'python app.py', ['startup', 'health'], ['started', 'healthy'])
    assert valid_runtime_verification(obj); print("[PASS] runtime verification built")
    assert bool(obj.task_id) and bool(obj.entrypoint) and bool(obj.checks) and bool(obj.observations); print("[PASS] contract data preserved")
    assert valid_runtime_verification(obj); print("[PASS] digest validates")
    tampered=RuntimeVerification("tampered", obj.entrypoint, obj.checks, obj.observations, obj.digest)
    assert not valid_runtime_verification(tampered); print("[PASS] tamper rejected")
    print("Setup 6.96 tests complete.")

if __name__=="__main__": main()
