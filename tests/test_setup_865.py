from services.phase8_865_migration_safety_gate import build_865,valid_865
def main():
    o=build_865("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_865(o) and o.valid() and o.setup=="8.65" and o.kind=="Migration Safety Gate"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_865(bad)
    try: build_865("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.65 Migration Safety Gate")
if __name__=="__main__": main()
