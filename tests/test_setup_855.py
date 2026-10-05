from services.phase8_855_safe_edit_transaction_planner import build_855,valid_855
def main():
    o=build_855("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_855(o) and o.valid() and o.setup=="8.55" and o.kind=="Safe Edit Transaction Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_855(bad)
    try: build_855("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.55 Safe Edit Transaction Planner")
if __name__=="__main__": main()
