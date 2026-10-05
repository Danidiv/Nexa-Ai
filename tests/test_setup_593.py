from services.completion_canary_rollout import build_canary_rollout, valid_canary_rollout, CanaryRollout

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.93 TEST")
    print("============================================================")
    obj = build_canary_rollout("sample", ["a", "b"], ["evidence"])
    assert valid_canary_rollout(obj); print("[PASS] canary stages built")
    assert obj.stages == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_canary_rollout(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["stages"] = ["tampered"]
    assert bad["stages"] != list(obj.stages) and not valid_canary_rollout(type(obj)(obj.name, tuple(bad["stages"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.93 tests complete.")

if __name__ == "__main__":
    main()
