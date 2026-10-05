from services.phase10_database_migration_executor import build_964, valid_964

def main():
    o=build_964("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"964"}, risk="low")
    assert valid_964(o) and o.valid() and o.setup=="964" and o.kind=="Database Migration Executor"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_964(bad)
    try: build_964("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 964 Database Migration Executor")

if __name__=="__main__": main()
