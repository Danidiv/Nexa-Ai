from services.phase7_756_frontend_architecture_plan import build_756, valid_756

def main():
    obj=build_756("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_756(obj)
    assert obj.setup == "7.56"
    assert obj.kind == "Frontend Architecture Plan"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_756(tampered)
    try:
        build_756("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.56 Frontend Architecture Plan")

if __name__ == "__main__": main()
