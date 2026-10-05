from services.phase10_data_migration_coordinator import build_978, valid_978

def main():
    o=build_978("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"978"}, risk="low")
    assert valid_978(o) and o.valid() and o.setup=="978" and o.kind=="Data Migration Coordinator"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_978(bad)
    try: build_978("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 978 Data Migration Coordinator")

if __name__=="__main__": main()
