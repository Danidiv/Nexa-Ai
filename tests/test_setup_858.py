from services.phase8_858_secret_exposure_guard import build_858,valid_858
def main():
    o=build_858("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_858(o) and o.valid() and o.setup=="8.58" and o.kind=="Secret Exposure Guard"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_858(bad)
    try: build_858("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.58 Secret Exposure Guard")
if __name__=="__main__": main()
