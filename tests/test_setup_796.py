from services.phase7_796_regression_repair_record import build_796, valid_796

def main():
    obj=build_796("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_796(obj)
    assert obj.setup == "7.96"
    assert obj.kind == "Regression Repair Record"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_796(tampered)
    try:
        build_796("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.96 Regression Repair Record")

if __name__ == "__main__": main()
