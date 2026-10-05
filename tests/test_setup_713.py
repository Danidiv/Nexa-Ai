from services.completion_api_plan import build_api_plan, valid_api_plan

def main():
    obj=build_api_plan("sample", **{f: [f"sample-{f}"] for f in ['routes', 'validation', 'responses']})
    assert valid_api_plan(obj)
    assert obj.kind == "api_plan"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.13 API Implementation Plan")

if __name__=="__main__": main()
