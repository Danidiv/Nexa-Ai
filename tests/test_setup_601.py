from services.completion_codebase_semantic_map import build_codebase_semantic_map, valid_codebase_semantic_map, CodebaseSemanticMap

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.01 TEST")
    print("============================================================")
    obj = build_codebase_semantic_map("sample", ["a", "b"], ["evidence"])
    assert valid_codebase_semantic_map(obj); print("[PASS] codebase semantic map built")
    assert obj.nodes == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_codebase_semantic_map(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["nodes"] = ["tampered"]
    assert not valid_codebase_semantic_map(CodebaseSemanticMap(obj.name, tuple(bad["nodes"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.01 tests complete.")

if __name__ == "__main__":
    main()
