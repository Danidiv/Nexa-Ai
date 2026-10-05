from services.phase8_806_product_context_assembly import build_806, valid_806

def main():
    obj=build_806("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_806(obj)
    assert obj.setup=="8.06"
    assert obj.kind=="Product Context Assembly"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_806(bad)
    try: build_806("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.06 Product Context Assembly")

if __name__=="__main__": main()
