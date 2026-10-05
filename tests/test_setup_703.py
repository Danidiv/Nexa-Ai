from services.completion_scope_map import build_scope_map, valid_scope_map

def main():
    obj=build_scope_map("sample", **{f: [f"sample-{f}"] for f in ['in_scope', 'out_of_scope', 'assumptions']})
    assert valid_scope_map(obj)
    assert obj.kind == "scope_map"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.03 Product Scope Mapping")

if __name__=="__main__": main()
