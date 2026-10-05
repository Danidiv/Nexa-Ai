from services.phase9_927_notification_system_planner import build_927,valid_927

def main():
    o=build_927("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.27","goal":"saas"},risk="low")
    assert valid_927(o) and o.valid() and o.setup=="9.27" and o.kind=="Notification System Planner"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_927(bad)
    try: build_927("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.27 Notification System Planner")

if __name__=="__main__": main()
