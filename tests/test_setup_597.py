from services.completion_data_migration_readiness import build_data_migration_readiness, valid_data_migration_readiness, DataMigrationReadiness

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.97 TEST")
    print("============================================================")
    obj = build_data_migration_readiness("sample", ["a", "b"], ["evidence"])
    assert valid_data_migration_readiness(obj); print("[PASS] migration plans built")
    assert obj.migrations == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_data_migration_readiness(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["migrations"] = ["tampered"]
    assert bad["migrations"] != list(obj.migrations) and not valid_data_migration_readiness(type(obj)(obj.name, tuple(bad["migrations"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.97 tests complete.")

if __name__ == "__main__":
    main()
