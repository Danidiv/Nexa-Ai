from services.phase8_876_incident_detection_model import build_876,valid_876
def main():
    o=build_876("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_876(o) and o.valid() and o.setup=="8.76" and o.kind=="Incident Detection Model"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_876(bad)
    try: build_876("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.76 Incident Detection Model")
if __name__=="__main__": main()
