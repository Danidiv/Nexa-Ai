from services.phase10_invoice_tax_abstraction import build_957, valid_957

def main():
    o=build_957("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"957"}, risk="low")
    assert valid_957(o) and o.valid() and o.setup=="957" and o.kind=="Invoice Tax Abstraction"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_957(bad)
    try: build_957("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 957 Invoice Tax Abstraction")

if __name__=="__main__": main()
