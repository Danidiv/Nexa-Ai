from services.phase10_billing_reconciliation_engine import build_956, valid_956

def main():
    o=build_956("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"956"}, risk="low")
    assert valid_956(o) and o.valid() and o.setup=="956" and o.kind=="Billing Reconciliation Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_956(bad)
    try: build_956("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 956 Billing Reconciliation Engine")

if __name__=="__main__": main()
