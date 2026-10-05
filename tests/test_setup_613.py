from services.completion_api_contract_inference import build_api_contract_inference, valid_api_contract_inference, ApiContractInference

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.13 TEST")
    print("============================================================")
    obj=build_api_contract_inference("sample",["a","b"],["evidence"]); assert valid_api_contract_inference(obj); print("[PASS] api contract inference built")
    assert obj.contracts == ("a","b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_api_contract_inference(obj); print("[PASS] digest validates")
    assert not valid_api_contract_inference(ApiContractInference(obj.name,("tampered",),obj.evidence,obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.13 tests complete.")
if __name__ == "__main__": main()
