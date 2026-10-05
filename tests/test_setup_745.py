from services.completion_release_candidate import build_release_candidate, valid_release_candidate

def main():
    obj=build_release_candidate("sample", **{f: [f"sample-{f}"] for f in ['artifacts', 'checks', 'status']})
    assert valid_release_candidate(obj)
    assert obj.kind == "release_candidate"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.45 Release Candidate Builder")

if __name__=="__main__": main()
