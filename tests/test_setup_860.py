from services.phase8_860_build_reproducibility_contract import build_860,valid_860
def main():
    o=build_860("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_860(o) and o.valid() and o.setup=="8.60" and o.kind=="Build Reproducibility Contract"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_860(bad)
    try: build_860("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.60 Build Reproducibility Contract")
if __name__=="__main__": main()
