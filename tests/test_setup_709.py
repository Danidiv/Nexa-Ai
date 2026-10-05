from services.completion_dependency_map import build_dependency_map, valid_dependency_map

def main():
    obj=build_dependency_map("sample", **{f: [f"sample-{f}"] for f in ['runtime', 'development', 'external']})
    assert valid_dependency_map(obj)
    assert obj.kind == "dependency_map"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.09 Dependency Mapping")

if __name__=="__main__": main()
