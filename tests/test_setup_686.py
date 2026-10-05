from services.completion_execution_sequencing import build_execution_sequencing, valid_execution_sequencing, ExecutionSequencing

def main():
    print("="*60); print("AZIZ AI SETUP 6.86 TEST"); print("="*60)
    obj=build_execution_sequencing('sample', ['edit', 'test', 'verify'], ['edit->test'], ['tests_pass'])
    assert valid_execution_sequencing(obj); print("[PASS] execution sequencing built")
    assert bool(obj.task_id) and bool(obj.steps) and bool(obj.dependencies) and bool(obj.barriers); print("[PASS] contract data preserved")
    assert valid_execution_sequencing(obj); print("[PASS] digest validates")
    tampered=ExecutionSequencing("tampered", obj.steps, obj.dependencies, obj.barriers, obj.digest)
    assert not valid_execution_sequencing(tampered); print("[PASS] tamper rejected")
    print("Setup 6.86 tests complete.")

if __name__=="__main__": main()
