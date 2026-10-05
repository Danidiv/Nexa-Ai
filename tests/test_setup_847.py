from services.phase8_847_product_quality_verification import build_847, valid_847

def main():
    obj=build_847("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_847(obj)
    assert obj.setup=="8.47"
    assert obj.kind=="Product Quality Verification"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_847(bad)
    try: build_847("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.47 Product Quality Verification")

if __name__=="__main__": main()
