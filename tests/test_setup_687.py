from services.completion_command_preflight import build_command_preflight, valid_command_preflight, CommandPreflight

def main():
    print("="*60); print("AZIZ AI SETUP 6.87 TEST"); print("="*60)
    obj=build_command_preflight('sample', ['python -m pytest'], ['python -m pytest'], [])
    assert valid_command_preflight(obj); print("[PASS] command preflight built")
    assert bool(obj.task_id) and bool(obj.commands) and bool(obj.allowed); print("[PASS] contract data preserved")
    assert valid_command_preflight(obj); print("[PASS] digest validates")
    tampered=CommandPreflight("tampered", obj.commands, obj.allowed, obj.blocked, obj.digest)
    assert not valid_command_preflight(tampered); print("[PASS] tamper rejected")
    print("Setup 6.87 tests complete.")

if __name__=="__main__": main()
