from services.completion_security_code_scan import build_security_code_scan, valid_security_code_scan, SecurityCodeScan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.15 TEST")
    print("============================================================")
    obj=build_security_code_scan("sample",["a","b"],["evidence"]); assert valid_security_code_scan(obj); print("[PASS] security code scan built")
    assert obj.findings == ("a","b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_security_code_scan(obj); print("[PASS] digest validates")
    assert not valid_security_code_scan(SecurityCodeScan(obj.name,("tampered",),obj.evidence,obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.15 tests complete.")
if __name__ == "__main__": main()
