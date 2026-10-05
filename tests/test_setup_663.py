from services.completion_context_budget import build_context_budget, valid_context_budget, ContextBudget

def main():
    print("="*60); print("AZIZ AI SETUP 6.63 TEST"); print("="*60)
    obj=build_context_budget("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_context_budget(obj); print("[PASS] context budget built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_context_budget(obj); print("[PASS] digest validates")
    tampered=ContextBudget("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_context_budget(tampered); print("[PASS] tamper rejected")
    print("Setup 6.63 tests complete.")

if __name__=="__main__": main()
