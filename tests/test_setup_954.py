from services.phase10_subscription_lifecycle_engine import build_954, valid_954

def main():
    o=build_954("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"954"}, risk="low")
    assert valid_954(o) and o.valid() and o.setup=="954" and o.kind=="Subscription Lifecycle Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_954(bad)
    try: build_954("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 954 Subscription Lifecycle Engine")

if __name__=="__main__": main()
