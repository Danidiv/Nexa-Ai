from services.completion_failure_recovery import build_failure_recovery, valid_failure_recovery

def main():
    obj=build_failure_recovery("sample", **{f: [f"sample-{f}"] for f in ['failure_classes', 'repairs', 'retry_limits']})
    assert valid_failure_recovery(obj)
    assert obj.kind == "failure_recovery"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.28 Failure Recovery Plan")

if __name__=="__main__": main()
