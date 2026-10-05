from services.phase7_794_browser_driven_implementation_record import build_794, valid_794

def main():
    obj=build_794("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_794(obj)
    assert obj.setup == "7.94"
    assert obj.kind == "Browser-Driven Implementation Record"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_794(tampered)
    try:
        build_794("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.94 Browser-Driven Implementation Record")

if __name__ == "__main__": main()
