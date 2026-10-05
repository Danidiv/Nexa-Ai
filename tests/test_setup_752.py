from services.phase7_752_user_story_model import build_752, valid_752

def main():
    obj=build_752("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_752(obj)
    assert obj.setup == "7.52"
    assert obj.kind == "User Story Model"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_752(tampered)
    try:
        build_752("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.52 User Story Model")

if __name__ == "__main__": main()
