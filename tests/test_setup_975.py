from services.phase10_alerting_engine import build_975, valid_975

def main():
    o=build_975("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"975"}, risk="low")
    assert valid_975(o) and o.valid() and o.setup=="975" and o.kind=="Alerting Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_975(bad)
    try: build_975("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 975 Alerting Engine")

if __name__=="__main__": main()
