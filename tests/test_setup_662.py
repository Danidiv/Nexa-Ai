from services.completion_tool_selection_policy import build_tool_selection_policy, valid_tool_selection_policy, ToolSelectionPolicy

def main():
    print("="*60); print("AZIZ AI SETUP 6.62 TEST"); print("="*60)
    obj=build_tool_selection_policy("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_tool_selection_policy(obj); print("[PASS] tool selection policy built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_tool_selection_policy(obj); print("[PASS] digest validates")
    tampered=ToolSelectionPolicy("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_tool_selection_policy(tampered); print("[PASS] tamper rejected")
    print("Setup 6.62 tests complete.")

if __name__=="__main__": main()
