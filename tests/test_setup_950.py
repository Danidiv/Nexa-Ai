from services.phase9_950_integrated_lovable_level_product_builder_v5 import build_950,valid_950

def main():
    o=build_950("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.50","goal":"saas"},risk="low")
    assert valid_950(o) and o.valid() and o.setup=="9.50" and o.kind=="Integrated Lovable-Level Product Builder V5"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_950(bad)
    try: build_950("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.50 Integrated Lovable-Level Product Builder V5")

if __name__=="__main__": main()
