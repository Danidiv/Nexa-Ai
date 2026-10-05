from services.phase10_security_remediation_engine import build_986, valid_986

def main():
    o=build_986("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"986"}, risk="low")
    assert valid_986(o) and o.valid() and o.setup=="986" and o.kind=="Security Remediation Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_986(bad)
    try: build_986("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 986 Security Remediation Engine")

if __name__=="__main__": main()
