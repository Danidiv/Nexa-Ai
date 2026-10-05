from services.completion_task_intent_extraction import build_task_intent_extraction, valid_task_intent_extraction, TaskIntentExtraction

def main():
    print("="*60); print("AZIZ AI SETUP 6.81 TEST"); print("="*60)
    obj=build_task_intent_extraction('sample', 'add login', ['python'], ['authentication'])
    assert valid_task_intent_extraction(obj); print("[PASS] task intent extraction built")
    assert bool(obj.task_id) and bool(obj.intent) and bool(obj.constraints) and bool(obj.signals); print("[PASS] contract data preserved")
    assert valid_task_intent_extraction(obj); print("[PASS] digest validates")
    tampered=TaskIntentExtraction("tampered", obj.intent, obj.constraints, obj.signals, obj.digest)
    assert not valid_task_intent_extraction(tampered); print("[PASS] tamper rejected")
    print("Setup 6.81 tests complete.")

if __name__=="__main__": main()
