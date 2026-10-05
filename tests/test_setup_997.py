from services.phase10_autonomous_product_session import build_997, valid_997

def main():
    o=build_997("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"997"}, risk="low")
    assert valid_997(o) and o.valid() and o.setup=="997" and o.kind=="Autonomous Product Session"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_997(bad)
    try: build_997("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 997 Autonomous Product Session")

if __name__=="__main__": main()
