from services.phase10_feedback_ingestion_engine import build_981, valid_981

def main():
    o=build_981("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"981"}, risk="low")
    assert valid_981(o) and o.valid() and o.setup=="981" and o.kind=="Feedback Ingestion Engine"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_981(bad)
    try: build_981("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 981 Feedback Ingestion Engine")

if __name__=="__main__": main()
