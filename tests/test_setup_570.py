from services.completion_preview_deployment_orchestrator import build_preview_deployment_orchestrator, valid_preview_deployment_orchestrator


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.70 TEST")
    print("============================================================")
    obj = build_preview_deployment_orchestrator("sample", ["a", "b"], ["evidence"])
    assert valid_preview_deployment_orchestrator(obj); print("[PASS] integrated preview/deployment workflow built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_preview_deployment_orchestrator(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_preview_deployment_orchestrator(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.70 tests complete.")

if __name__ == "__main__":
    main()
