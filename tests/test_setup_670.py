from services.completion_rollback_transaction import build_rollback_transaction, valid_rollback_transaction, RollbackTransaction

def main():
    print("="*60); print("AZIZ AI SETUP 6.70 TEST"); print("="*60)
    obj=build_rollback_transaction("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_rollback_transaction(obj); print("[PASS] rollback transaction built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_rollback_transaction(obj); print("[PASS] digest validates")
    tampered=RollbackTransaction("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_rollback_transaction(tampered); print("[PASS] tamper rejected")
    print("Setup 6.70 tests complete.")

if __name__=="__main__": main()
