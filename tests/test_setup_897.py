from services.phase8_897_service_ownership_registry import build_897,valid_897
def main():
    o=build_897("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_897(o) and o.valid() and o.setup=="8.97" and o.kind=="Service Ownership Registry"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_897(bad)
    try: build_897("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.97 Service Ownership Registry")
if __name__=="__main__": main()
