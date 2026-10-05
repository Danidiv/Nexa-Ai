from services.completion_failure_clustering import build_failure_clustering, valid_failure_clustering, FailureClustering

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.07 TEST")
    print("============================================================")
    obj = build_failure_clustering("sample", ["a", "b"], ["evidence"])
    assert valid_failure_clustering(obj); print("[PASS] failure clustering built")
    assert obj.clusters == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_failure_clustering(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["clusters"] = ["tampered"]
    assert not valid_failure_clustering(FailureClustering(obj.name, tuple(bad["clusters"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.07 tests complete.")

if __name__ == "__main__":
    main()
