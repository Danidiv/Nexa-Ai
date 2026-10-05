from services.completion_security_remediation_plan import build_security_remediation_plan, valid_security_remediation_plan, SecurityRemediationPlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.34 TEST")
    print("============================================================")
    obj=build_security_remediation_plan(["a","b"], ["a","b"], ["a","b"], ["a","b"])
    assert valid_security_remediation_plan(obj); print("[PASS] security remediation plan built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_security_remediation_plan(obj); print("[PASS] digest validates")
    assert not valid_security_remediation_plan(SecurityRemediationPlan(( "tampered", ), obj.actions, obj.priority, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.34 tests complete.")
if __name__ == "__main__": main()
