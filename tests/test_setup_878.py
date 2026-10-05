from services.phase8_878_automated_remediation_guard import build_878,valid_878
def main():
    o=build_878("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_878(o) and o.valid() and o.setup=="8.78" and o.kind=="Automated Remediation Guard"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_878(bad)
    try: build_878("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.78 Automated Remediation Guard")
if __name__=="__main__": main()
