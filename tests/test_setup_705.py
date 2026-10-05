from services.completion_architecture_discovery import build_architecture_discovery, valid_architecture_discovery

def main():
    obj=build_architecture_discovery("sample", **{f: [f"sample-{f}"] for f in ['frontend', 'backend', 'database']})
    assert valid_architecture_discovery(obj)
    assert obj.kind == "architecture_discovery"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.05 Architecture Discovery")

if __name__=="__main__": main()
