from services.completion_verification_bundle import build_verification_bundle, valid_verification_bundle

def main():
    obj=build_verification_bundle("sample", **{f: [f"sample-{f}"] for f in ['browser', 'visual', 'console', 'flows']})
    assert valid_verification_bundle(obj)
    assert obj.kind == "verification_bundle"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.40 Product Verification Bundle")

if __name__=="__main__": main()
