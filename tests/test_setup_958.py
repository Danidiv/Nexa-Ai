from services.phase10_support_admin_action_guard import build_958, valid_958

def main():
    o=build_958("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"958"}, risk="low")
    assert valid_958(o) and o.valid() and o.setup=="958" and o.kind=="Support Admin Action Guard"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_958(bad)
    try: build_958("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 958 Support Admin Action Guard")

if __name__=="__main__": main()
