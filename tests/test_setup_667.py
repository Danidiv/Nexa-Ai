from services.completion_failure_action_mapping import build_failure_action_mapping, valid_failure_action_mapping, FailureActionMapping

def main():
    print("="*60); print("AZIZ AI SETUP 6.67 TEST"); print("="*60)
    obj=build_failure_action_mapping("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_failure_action_mapping(obj); print("[PASS] failure-to-action mapping built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_failure_action_mapping(obj); print("[PASS] digest validates")
    tampered=FailureActionMapping("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_failure_action_mapping(tampered); print("[PASS] tamper rejected")
    print("Setup 6.67 tests complete.")

if __name__=="__main__": main()
