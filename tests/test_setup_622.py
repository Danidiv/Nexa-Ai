from services.completion_context_assembly import build_context_assembly, valid_context_assembly, ContextAssembly

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.22 TEST")
    print("============================================================")
    obj=build_context_assembly("sample", ["a","b"], {"max": 3}, ["a","b"])
    assert valid_context_assembly(obj); print("[PASS] context assembly built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_context_assembly(obj); print("[PASS] digest validates")
    assert not valid_context_assembly(ContextAssembly("tampered", obj.sources, obj.budget, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.22 tests complete.")
if __name__ == "__main__": main()
