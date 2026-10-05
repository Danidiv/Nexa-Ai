from services.completion_integration_plan import build_integration_plan, valid_integration_plan

def main():
    obj=build_integration_plan("sample", **{f: [f"sample-{f}"] for f in ['integrations', 'adapters', 'fallbacks']})
    assert valid_integration_plan(obj)
    assert obj.kind == "integration_plan"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.16 Integration Implementation Plan")

if __name__=="__main__": main()
