from services.completion_outcome_learning import build_outcome_learning, valid_outcome_learning, OutcomeLearning

def main():
    print("="*60); print("AZIZ AI SETUP 6.98 TEST"); print("="*60)
    obj=build_outcome_learning('sample', ['pytest before edit'], ['targeted repair'], ['broad edit avoided'])
    assert valid_outcome_learning(obj); print("[PASS] outcome learning built")
    assert bool(obj.task_id) and bool(obj.patterns) and bool(obj.successes) and bool(obj.failures); print("[PASS] contract data preserved")
    assert valid_outcome_learning(obj); print("[PASS] digest validates")
    tampered=OutcomeLearning("tampered", obj.patterns, obj.successes, obj.failures, obj.digest)
    assert not valid_outcome_learning(tampered); print("[PASS] tamper rejected")
    print("Setup 6.98 tests complete.")

if __name__=="__main__": main()
