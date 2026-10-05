from services.completion_integrated_software_engineering_agent import build_integrated_software_engineering_agent, valid_integrated_software_engineering_agent, IntegratedSoftwareEngineeringAgent

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.20 TEST")
    print("============================================================")
    obj=build_integrated_software_engineering_agent("sample",["a","b"],["evidence"]); assert valid_integrated_software_engineering_agent(obj); print("[PASS] integrated software engineering agent built")
    assert obj.capabilities == ("a","b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_integrated_software_engineering_agent(obj); print("[PASS] digest validates")
    assert not valid_integrated_software_engineering_agent(IntegratedSoftwareEngineeringAgent(obj.name,("tampered",),obj.evidence,obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.20 tests complete.")
if __name__ == "__main__": main()
