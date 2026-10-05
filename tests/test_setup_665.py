from services.completion_command_execution_record import build_command_execution_record, valid_command_execution_record, CommandExecutionRecord

def main():
    print("="*60); print("AZIZ AI SETUP 6.65 TEST"); print("="*60)
    obj=build_command_execution_record("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_command_execution_record(obj); print("[PASS] command execution record built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_command_execution_record(obj); print("[PASS] digest validates")
    tampered=CommandExecutionRecord("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_command_execution_record(tampered); print("[PASS] tamper rejected")
    print("Setup 6.65 tests complete.")

if __name__=="__main__": main()
