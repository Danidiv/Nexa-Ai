from services.phase9_929_file_storage_planner import build_929,valid_929

def main():
    o=build_929("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.29","goal":"saas"},risk="low")
    assert valid_929(o) and o.valid() and o.setup=="9.29" and o.kind=="File Storage Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_929(bad)
    try: build_929("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.29 File Storage Planner")

if __name__=="__main__": main()
