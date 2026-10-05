from services.phase10_customer_onboarding_workflow import build_951, valid_951

def main():
    o=build_951("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"951"}, risk="low")
    assert valid_951(o) and o.valid() and o.setup=="951" and o.kind=="Customer Onboarding Workflow"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_951(bad)
    try: build_951("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 951 Customer Onboarding Workflow")

if __name__=="__main__": main()
