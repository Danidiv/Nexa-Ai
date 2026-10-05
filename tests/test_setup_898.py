from services.phase8_898_production_knowledge_memory import build_898,valid_898
def main():
    o=build_898("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_898(o) and o.valid() and o.setup=="8.98" and o.kind=="Production Knowledge Memory"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_898(bad)
    try: build_898("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.98 Production Knowledge Memory")
if __name__=="__main__": main()
