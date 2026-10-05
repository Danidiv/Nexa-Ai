from services.phase8_877_incident_response_plan import build_877,valid_877
def main():
    o=build_877("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_877(o) and o.valid() and o.setup=="8.77" and o.kind=="Incident Response Plan"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_877(bad)
    try: build_877("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.77 Incident Response Plan")
if __name__=="__main__": main()
