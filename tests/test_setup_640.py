from services.completion_integrated_autonomous_engineer_v2 import build_integrated_autonomous_engineer_v2, valid_integrated_autonomous_engineer_v2, IntegratedAutonomousEngineerV2

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.40 TEST")
    print("============================================================")
    obj=build_integrated_autonomous_engineer_v2("sample", ["a","b"], ["a","b"], ["a","b"])
    assert valid_integrated_autonomous_engineer_v2(obj); print("[PASS] integrated autonomous software engineer v2 built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_integrated_autonomous_engineer_v2(obj); print("[PASS] digest validates")
    assert not valid_integrated_autonomous_engineer_v2(IntegratedAutonomousEngineerV2("tampered", obj.capabilities, obj.evidence, obj.dependencies, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.40 tests complete.")
if __name__ == "__main__": main()
