from services.phase8_882_feedback_requirement_mapper import build_882,valid_882
def main():
    o=build_882("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_882(o) and o.valid() and o.setup=="8.82" and o.kind=="Feedback-to-Requirement Mapper"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_882(bad)
    try: build_882("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.82 Feedback-to-Requirement Mapper")
if __name__=="__main__": main()
