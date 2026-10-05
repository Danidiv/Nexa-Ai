from services.completion_requirements import build_requirements, valid_requirements

def main():
    obj=build_requirements("sample", **{f: [f"sample-{f}"] for f in ['intent', 'constraints', 'acceptance']})
    assert valid_requirements(obj)
    assert obj.kind == "requirements"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.01 Requirement Intake")

if __name__=="__main__": main()
