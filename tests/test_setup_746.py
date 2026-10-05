from services.completion_handoff import build_handoff, valid_handoff

def main():
    obj=build_handoff("sample", **{f: [f"sample-{f}"] for f in ['summary', 'changes', 'verification']})
    assert valid_handoff(obj)
    assert obj.kind == "handoff"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.46 Project Handoff Package")

if __name__=="__main__": main()
