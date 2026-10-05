from services.completion_post_deploy_verification import build_post_deploy_verification, valid_post_deploy_verification


def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.86 TEST")
    print("============================================================")
    obj = build_post_deploy_verification("sample", ["a", "b"], ["evidence"])
    assert valid_post_deploy_verification(obj); print("[PASS] post-deploy verification built")
    assert obj.items == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_post_deploy_verification(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["items"] = ["tampered"]
    assert bad["items"] != list(obj.items) and not valid_post_deploy_verification(type(obj)(obj.name, tuple(bad["items"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.86 tests complete.")

if __name__ == "__main__":
    main()
