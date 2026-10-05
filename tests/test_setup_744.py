from services.completion_quality_score import build_quality_score, valid_quality_score

def main():
    obj=build_quality_score("sample", **{f: [f"sample-{f}"] for f in ['functional', 'visual', 'runtime', 'security']})
    assert valid_quality_score(obj)
    assert obj.kind == "quality_score"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.44 Product Quality Score")

if __name__=="__main__": main()
