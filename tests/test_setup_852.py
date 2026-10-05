from services.phase8_852_technical_task_decomposition import build_852,valid_852
def main():
    o=build_852("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_852(o) and o.valid() and o.setup=="8.52" and o.kind=="Technical Task Decomposition"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_852(bad)
    try: build_852("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.52 Technical Task Decomposition")
if __name__=="__main__": main()
