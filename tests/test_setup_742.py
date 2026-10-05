from services.completion_repair_gate import build_repair_gate, valid_repair_gate

def main():
    obj=build_repair_gate("sample", **{f: [f"sample-{f}"] for f in ['risk', 'scope', 'required_evidence']})
    assert valid_repair_gate(obj)
    assert obj.kind == "repair_gate"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.42 Repair Safety Gate")

if __name__=="__main__": main()
