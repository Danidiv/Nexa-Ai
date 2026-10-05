from services.completion_test_orchestration import build_test_orchestration, valid_test_orchestration

def main():
    obj=build_test_orchestration("sample", **{f: [f"sample-{f}"] for f in ['suites', 'priority', 'stop_conditions']})
    assert valid_test_orchestration(obj)
    assert obj.kind == "test_orchestration"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.27 Test Orchestration Plan")

if __name__=="__main__": main()
