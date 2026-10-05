from services.completion_task_outcome_scorer import build_task_outcome_scorer, valid_task_outcome_scorer, TaskOutcomeScorer

def main():
    print("="*60); print("AZIZ AI SETUP 6.77 TEST"); print("="*60)
    obj=build_task_outcome_scorer("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_task_outcome_scorer(obj); print("[PASS] task outcome scorer built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_task_outcome_scorer(obj); print("[PASS] digest validates")
    tampered=TaskOutcomeScorer("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_task_outcome_scorer(tampered); print("[PASS] tamper rejected")
    print("Setup 6.77 tests complete.")

if __name__=="__main__": main()
