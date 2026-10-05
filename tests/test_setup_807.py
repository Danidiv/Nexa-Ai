from services.phase8_807_architecture_constraint_solver import build_807, valid_807

def main():
    obj=build_807("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_807(obj)
    assert obj.setup=="8.07"
    assert obj.kind=="Architecture Constraint Solver"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_807(bad)
    try: build_807("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.07 Architecture Constraint Solver")

if __name__=="__main__": main()
