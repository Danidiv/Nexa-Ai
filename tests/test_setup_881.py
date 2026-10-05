from services.phase8_881_user_feedback_intake import build_881,valid_881
def main():
    o=build_881("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_881(o) and o.valid() and o.setup=="8.81" and o.kind=="User Feedback Intake"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_881(bad)
    try: build_881("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.81 User Feedback Intake")
if __name__=="__main__": main()
