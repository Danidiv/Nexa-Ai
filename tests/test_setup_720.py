from services.completion_implementation_bundle import build_implementation_bundle, valid_implementation_bundle

def main():
    obj=build_implementation_bundle("sample", **{f: [f"sample-{f}"] for f in ['frontend', 'backend', 'api', 'database', 'auth', 'ordering']})
    assert valid_implementation_bundle(obj)
    assert obj.kind == "implementation_bundle"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.20 Full-Stack Implementation Bundle")

if __name__=="__main__": main()
