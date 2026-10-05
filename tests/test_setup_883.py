from services.phase8_883_product_analytics_contract import build_883,valid_883
def main():
    o=build_883("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_883(o) and o.valid() and o.setup=="8.83" and o.kind=="Product Analytics Contract"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_883(bad)
    try: build_883("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.83 Product Analytics Contract")
if __name__=="__main__": main()
