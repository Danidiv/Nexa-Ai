from services.completion_validation_plan import build_validation_plan, valid_validation_plan

def main():
    obj=build_validation_plan("sample", **{f: [f"sample-{f}"] for f in ['client', 'server', 'rules']})
    assert valid_validation_plan(obj)
    assert obj.kind == "validation_plan"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.18 Validation Implementation Plan")

if __name__=="__main__": main()
