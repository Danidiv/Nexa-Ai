from services.phase10_backup_restore_executor import build_977, valid_977

def main():
    o=build_977("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"977"}, risk="low")
    assert valid_977(o) and o.valid() and o.setup=="977" and o.kind=="Backup Restore Executor"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_977(bad)
    try: build_977("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 977 Backup Restore Executor")

if __name__=="__main__": main()
