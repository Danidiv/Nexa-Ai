from services.completion_normalized_requirements import build_normalized_requirements, valid_normalized_requirements

def main():
    obj=build_normalized_requirements("sample", **{f: [f"sample-{f}"] for f in ['goal', 'features', 'constraints']})
    assert valid_normalized_requirements(obj)
    assert obj.kind == "normalized_requirements"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.02 Requirement Normalization")

if __name__=="__main__": main()
