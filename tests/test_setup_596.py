from services.completion_backup_restore_readiness import build_backup_restore_readiness, valid_backup_restore_readiness, BackupRestoreReadiness

def main():
    print("============================================================")
    print("AZIZ AI SETUP 5.96 TEST")
    print("============================================================")
    obj = build_backup_restore_readiness("sample", ["a", "b"], ["evidence"])
    assert valid_backup_restore_readiness(obj); print("[PASS] restore checkpoints built")
    assert obj.checkpoints == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_backup_restore_readiness(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["checkpoints"] = ["tampered"]
    assert bad["checkpoints"] != list(obj.checkpoints) and not valid_backup_restore_readiness(type(obj)(obj.name, tuple(bad["checkpoints"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 5.96 tests complete.")

if __name__ == "__main__":
    main()
