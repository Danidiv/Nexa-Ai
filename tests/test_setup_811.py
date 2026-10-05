from services.phase8_811_api_contract_synthesis import build_811, valid_811

def main():
    obj=build_811("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_811(obj)
    assert obj.setup=="8.11"
    assert obj.kind=="API Contract Synthesis"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_811(bad)
    try: build_811("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.11 API Contract Synthesis")

if __name__=="__main__": main()
