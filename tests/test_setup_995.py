from services.phase10_final_verification_engine import build_995, valid_995

def main():
    o=build_995("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"995"}, risk="low")
    assert valid_995(o) and o.valid() and o.setup=="995" and o.kind=="Final Verification Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_995(bad)
    try: build_995("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 995 Final Verification Engine")

if __name__=="__main__": main()
