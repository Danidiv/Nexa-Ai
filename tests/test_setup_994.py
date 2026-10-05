from services.phase10_human_escalation_controller import build_994, valid_994

def main():
    o=build_994("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"994"}, risk="low")
    assert valid_994(o) and o.valid() and o.setup=="994" and o.kind=="Human Escalation Controller"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_994(bad)
    try: build_994("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 994 Human Escalation Controller")

if __name__=="__main__": main()
