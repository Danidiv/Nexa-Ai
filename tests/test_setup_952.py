from services.phase10_organization_workspace_lifecycle import build_952, valid_952

def main():
    o=build_952("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"952"}, risk="low")
    assert valid_952(o) and o.valid() and o.setup=="952" and o.kind=="Organization Workspace Lifecycle"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_952(bad)
    try: build_952("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 952 Organization Workspace Lifecycle")

if __name__=="__main__": main()
