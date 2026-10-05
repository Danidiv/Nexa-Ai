from services.phase10_learned_playbook_registry import build_990, valid_990

def main():
    o=build_990("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"990"}, risk="low")
    assert valid_990(o) and o.valid() and o.setup=="990" and o.kind=="Learned Playbook Registry"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_990(bad)
    try: build_990("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 990 Learned Playbook Registry")

if __name__=="__main__": main()
