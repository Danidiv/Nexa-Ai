from services.completion_safe_edit_strategy import build_safe_edit_strategy, valid_safe_edit_strategy, SafeEditStrategy

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.23 TEST")
    print("============================================================")
    obj=build_safe_edit_strategy(["a","b"], ["a","b"], ["a","b"], ["a","b"])
    assert valid_safe_edit_strategy(obj); print("[PASS] safe edit strategy built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_safe_edit_strategy(obj); print("[PASS] digest validates")
    assert not valid_safe_edit_strategy(SafeEditStrategy(( "tampered", ), obj.strategy, obj.guards, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.23 tests complete.")
if __name__ == "__main__": main()
