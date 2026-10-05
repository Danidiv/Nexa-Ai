from services.phase10_role_permission_compiler import build_953, valid_953

def main():
    o=build_953("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"953"}, risk="low")
    assert valid_953(o) and o.valid() and o.setup=="953" and o.kind=="Role Permission Compiler"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_953(bad)
    try: build_953("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 953 Role Permission Compiler")

if __name__=="__main__": main()
