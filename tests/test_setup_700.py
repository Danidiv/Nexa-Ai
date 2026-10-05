from services.completion_autonomous_engineer_v3 import build_autonomous_engineer_v3, valid_autonomous_engineer_v3, AutonomousEngineerV3

def main():
    print("="*60); print("AZIZ AI SETUP 7.00 TEST"); print("="*60)
    obj=build_autonomous_engineer_v3('sample', 'add login', ['app.py'], ['edit', 'test'], ['run', 'repair'], ['verified'], ['learned'], 'completed')
    assert valid_autonomous_engineer_v3(obj); print("[PASS] integrated autonomous engineer v3 built")
    assert bool(obj.task_id) and bool(obj.intent) and bool(obj.targets) and bool(obj.plan) and bool(obj.execution) and bool(obj.verification) and bool(obj.learning) and bool(obj.status); print("[PASS] contract data preserved")
    assert valid_autonomous_engineer_v3(obj); print("[PASS] digest validates")
    tampered=AutonomousEngineerV3("tampered", obj.intent, obj.targets, obj.plan, obj.execution, obj.verification, obj.learning, obj.status, obj.digest)
    assert not valid_autonomous_engineer_v3(tampered); print("[PASS] tamper rejected")
    print("Setup 7.00 tests complete.")

if __name__=="__main__": main()
