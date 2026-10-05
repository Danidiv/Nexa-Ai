from services.completion_integrated_engineering_orchestrator import build_integrated_engineering_orchestrator, valid_integrated_engineering_orchestrator, IntegratedEngineeringOrchestrator

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.60 TEST")
    print("============================================================")
    obj=build_integrated_engineering_orchestrator("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_integrated_engineering_orchestrator(obj); print("[PASS] integrated engineering orchestrator built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_integrated_engineering_orchestrator(obj); print("[PASS] digest validates")
    tampered=IntegratedEngineeringOrchestrator("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_integrated_engineering_orchestrator(tampered); print("[PASS] tamper rejected")
    print("Setup 6.60 tests complete.")

if __name__ == "__main__": main()
