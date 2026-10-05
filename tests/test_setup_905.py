from services.phase9_905_session_security_guard import build_905,valid_905

def main():
    o=build_905("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.05","goal":"saas"},risk="low")
    assert valid_905(o) and o.valid() and o.setup=="9.05" and o.kind=="Session Security Guard"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_905(bad)
    try: build_905("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.05 Session Security Guard")

if __name__=="__main__": main()
