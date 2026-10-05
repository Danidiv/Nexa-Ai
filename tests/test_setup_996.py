from services.phase10_release_evidence_synthesizer import build_996, valid_996

def main():
    o=build_996("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"996"}, risk="low")
    assert valid_996(o) and o.valid() and o.setup=="996" and o.kind=="Release Evidence Synthesizer"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_996(bad)
    try: build_996("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 996 Release Evidence Synthesizer")

if __name__=="__main__": main()
