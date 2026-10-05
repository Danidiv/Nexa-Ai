from services.phase8_829_repair_candidate_engine import build_829, valid_829

def main():
    obj=build_829("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_829(obj)
    assert obj.setup=="8.29"
    assert obj.kind=="Autonomous Repair Candidate Engine"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_829(bad)
    try: build_829("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.29 Autonomous Repair Candidate Engine")

if __name__=="__main__": main()
