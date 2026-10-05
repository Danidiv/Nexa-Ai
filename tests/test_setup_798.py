from services.phase7_798_completion_evidence_bundle import build_798, valid_798

def main():
    obj=build_798("sample", goal="build product", evidence=["planned","verified"], status="ready")
    assert valid_798(obj)
    assert obj.setup == "7.98"
    assert obj.kind == "Completion Evidence Bundle"
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_798(tampered)
    try:
        build_798("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 7.98 Completion Evidence Bundle")

if __name__ == "__main__": main()
