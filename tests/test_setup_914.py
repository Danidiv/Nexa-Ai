from services.phase9_914_database_integrity_guard import build_914,valid_914

def main():
    o=build_914("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.14","goal":"saas"},risk="low")
    assert valid_914(o) and o.valid() and o.setup=="9.14" and o.kind=="Database Integrity Guard"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_914(bad)
    try: build_914("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.14 Database Integrity Guard")

if __name__=="__main__": main()
