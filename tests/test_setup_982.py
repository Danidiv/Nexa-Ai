from services.phase10_requirement_change_compiler import build_982, valid_982

def main():
    o=build_982("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"982"}, risk="low")
    assert valid_982(o) and o.valid() and o.setup=="982" and o.kind=="Requirement Change Compiler"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_982(bad)
    try: build_982("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 982 Requirement Change Compiler")

if __name__=="__main__": main()
