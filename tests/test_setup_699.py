from services.completion_autonomous_session_controller import build_autonomous_session_controller, valid_autonomous_session_controller, AutonomousSessionController

def main():
    print("="*60); print("AZIZ AI SETUP 6.99 TEST"); print("="*60)
    obj=build_autonomous_session_controller('sample', ['understand', 'plan', 'modify', 'test', 'repair', 'verify'], 'verify', 'active')
    assert valid_autonomous_session_controller(obj); print("[PASS] autonomous session controller built")
    assert bool(obj.task_id) and bool(obj.phases) and bool(obj.current) and bool(obj.status); print("[PASS] contract data preserved")
    assert valid_autonomous_session_controller(obj); print("[PASS] digest validates")
    tampered=AutonomousSessionController("tampered", obj.phases, obj.current, obj.status, obj.digest)
    assert not valid_autonomous_session_controller(tampered); print("[PASS] tamper rejected")
    print("Setup 6.99 tests complete.")

if __name__=="__main__": main()
