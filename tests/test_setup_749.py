from services.completion_builder_runtime import build_builder_runtime, valid_builder_runtime

def main():
    obj=build_builder_runtime("sample", **{f: [f"sample-{f}"] for f in ['phases', 'state', 'evidence']})
    assert valid_builder_runtime(obj)
    assert obj.kind == "builder_runtime"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.49 Product Builder Runtime")

if __name__=="__main__": main()
