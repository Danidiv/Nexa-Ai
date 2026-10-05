from services.phase8_864_release_artifact_manifest import build_864,valid_864
def main():
    o=build_864("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_864(o) and o.valid() and o.setup=="8.64" and o.kind=="Release Artifact Manifest"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_864(bad)
    try: build_864("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.64 Release Artifact Manifest")
if __name__=="__main__": main()
