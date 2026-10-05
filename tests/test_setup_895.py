from services.phase8_895_backup_recovery_contract import build_895,valid_895
def main():
    o=build_895("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_895(o) and o.valid() and o.setup=="8.95" and o.kind=="Backup Recovery Contract"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_895(bad)
    try: build_895("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.95 Backup Recovery Contract")
if __name__=="__main__": main()
