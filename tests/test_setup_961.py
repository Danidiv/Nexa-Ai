from services.phase10_scaffolding_compiler import build_961, valid_961

def main():
    o=build_961("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"961"}, risk="low")
    assert valid_961(o) and o.valid() and o.setup=="961" and o.kind=="Scaffolding Compiler"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_961(bad)
    try: build_961("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 961 Scaffolding Compiler")

if __name__=="__main__": main()
