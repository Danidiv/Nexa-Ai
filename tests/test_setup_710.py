from services.completion_understanding_bundle import build_understanding_bundle, valid_understanding_bundle

def main():
    obj=build_understanding_bundle("sample", **{f: [f"sample-{f}"] for f in ['requirements', 'scope', 'architecture', 'ui', 'api', 'data']})
    assert valid_understanding_bundle(obj)
    assert obj.kind == "understanding_bundle"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.10 Product Understanding Bundle")

if __name__=="__main__": main()
