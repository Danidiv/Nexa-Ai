from services.completion_call_graph import build_call_graph, valid_call_graph, CallGraph

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.03 TEST")
    print("============================================================")
    obj = build_call_graph("sample", ["a", "b"], ["evidence"])
    assert valid_call_graph(obj); print("[PASS] call graph built")
    assert obj.edges == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_call_graph(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["edges"] = ["tampered"]
    assert not valid_call_graph(CallGraph(obj.name, tuple(bad["edges"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.03 tests complete.")

if __name__ == "__main__":
    main()
