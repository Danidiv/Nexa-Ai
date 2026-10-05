from services.completion_execution_graph import build_execution_graph, valid_execution_graph, ExecutionGraph

def main():
    print("="*60); print("AZIZ AI SETUP 6.61 TEST"); print("="*60)
    obj=build_execution_graph("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_execution_graph(obj); print("[PASS] execution graph built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_execution_graph(obj); print("[PASS] digest validates")
    tampered=ExecutionGraph("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_execution_graph(tampered); print("[PASS] tamper rejected")
    print("Setup 6.61 tests complete.")

if __name__=="__main__": main()
