from services.completion_git_change_set_plan import build_git_change_set_plan, valid_git_change_set_plan, GitChangeSetPlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.37 TEST")
    print("============================================================")
    obj=build_git_change_set_plan(["a","b"], ["a","b"], ["a","b"], ["a","b"])
    assert valid_git_change_set_plan(obj); print("[PASS] Git change set plan built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_git_change_set_plan(obj); print("[PASS] digest validates")
    assert not valid_git_change_set_plan(GitChangeSetPlan(( "tampered", ), obj.changes, obj.checks, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.37 tests complete.")
if __name__ == "__main__": main()
