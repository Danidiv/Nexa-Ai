from services.completion_autonomous_operations_coordinator import build_autonomous_operations_coordinator, valid_autonomous_operations_coordinator, AutonomousOperationsCoordinator

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.00 TEST")
    print("============================================================")
    obj = build_autonomous_operations_coordinator("sample", ["a", "b"], ["evidence"])
    assert valid_autonomous_operations_coordinator(obj); print("[PASS] operations tracks built")
    assert obj.tracks == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_autonomous_operations_coordinator(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["tracks"] = ["tampered"]
    assert bad["tracks"] != list(obj.tracks) and not valid_autonomous_operations_coordinator(type(obj)(obj.name, tuple(bad["tracks"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.00 tests complete.")

if __name__ == "__main__":
    main()
