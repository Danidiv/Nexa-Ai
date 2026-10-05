from services.phase10_saas_delivery_foundation import build_960, valid_960

def main():
    o=build_960("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"960"}, risk="low")
    assert valid_960(o) and o.valid() and o.setup=="960" and o.kind=="SaaS Delivery Foundation"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_960(bad)
    try: build_960("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 960 SaaS Delivery Foundation")

if __name__=="__main__": main()
