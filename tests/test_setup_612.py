from services.completion_change_validation import build_change_validation, valid_change_validation, ChangeValidation

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.12 TEST")
    print("============================================================")
    obj=build_change_validation("sample",["a","b"],["evidence"]); assert valid_change_validation(obj); print("[PASS] change validation built")
    assert obj.checks == ("a","b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_change_validation(obj); print("[PASS] digest validates")
    assert not valid_change_validation(ChangeValidation(obj.name,("tampered",),obj.evidence,obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.12 tests complete.")
if __name__ == "__main__": main()
