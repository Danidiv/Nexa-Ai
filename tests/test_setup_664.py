from services.completion_workspace_change_journal import build_workspace_change_journal, valid_workspace_change_journal, WorkspaceChangeJournal

def main():
    print("="*60); print("AZIZ AI SETUP 6.64 TEST"); print("="*60)
    obj=build_workspace_change_journal("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_workspace_change_journal(obj); print("[PASS] workspace change journal built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_workspace_change_journal(obj); print("[PASS] digest validates")
    tampered=WorkspaceChangeJournal("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_workspace_change_journal(tampered); print("[PASS] tamper rejected")
    print("Setup 6.64 tests complete.")

if __name__=="__main__": main()
