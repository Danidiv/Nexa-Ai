from services.phase8_840_autonomous_product_qa import build_840, valid_840

def main():
    obj=build_840("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_840(obj)
    assert obj.setup=="8.40"
    assert obj.kind=="Autonomous Product QA Engine"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_840(bad)
    try: build_840("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.40 Autonomous Product QA Engine")

if __name__=="__main__": main()
