from services.completion_edit_plan_validation import build_edit_plan_validation, valid_edit_plan_validation, EditPlanValidation

def main():
    print("="*60); print("AZIZ AI SETUP 6.85 TEST"); print("="*60)
    obj=build_edit_plan_validation('sample', ['app.py'], ['file exists'], ['medium'])
    assert valid_edit_plan_validation(obj); print("[PASS] edit plan validation built")
    assert bool(obj.task_id) and bool(obj.edits) and bool(obj.preconditions) and bool(obj.risks); print("[PASS] contract data preserved")
    assert valid_edit_plan_validation(obj); print("[PASS] digest validates")
    tampered=EditPlanValidation("tampered", obj.edits, obj.preconditions, obj.risks, obj.digest)
    assert not valid_edit_plan_validation(tampered); print("[PASS] tamper rejected")
    print("Setup 6.85 tests complete.")

if __name__=="__main__": main()
