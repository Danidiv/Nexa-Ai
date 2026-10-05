from services.completion_project_discovery import build_project_discovery, valid_project_discovery

def main():
    obj=build_project_discovery("sample", **{f: [f"sample-{f}"] for f in ['root', 'files', 'entry_points']})
    assert valid_project_discovery(obj)
    assert obj.kind == "project_discovery"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.04 Project Discovery")

if __name__=="__main__": main()
