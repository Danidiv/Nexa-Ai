from services.completion_data_flow_analysis import build_data_flow_analysis, valid_data_flow_analysis, DataFlowAnalysis

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.14 TEST")
    print("============================================================")
    obj=build_data_flow_analysis("sample",["a","b"],["evidence"]); assert valid_data_flow_analysis(obj); print("[PASS] data flow analysis built")
    assert obj.flows == ("a","b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_data_flow_analysis(obj); print("[PASS] digest validates")
    assert not valid_data_flow_analysis(DataFlowAnalysis(obj.name,("tampered",),obj.evidence,obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.14 tests complete.")
if __name__ == "__main__": main()
