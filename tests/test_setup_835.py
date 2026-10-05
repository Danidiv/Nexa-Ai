from services.phase8_835_responsive_qa_coordinator import build_835, valid_835

def main():
    obj=build_835("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_835(obj)
    assert obj.setup=="8.35"
    assert obj.kind=="Responsive QA Coordinator"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_835(bad)
    try: build_835("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.35 Responsive QA Coordinator")

if __name__=="__main__": main()
