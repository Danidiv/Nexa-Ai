from services.completion_symbol_index import build_symbol_index, valid_symbol_index, SymbolIndex

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.02 TEST")
    print("============================================================")
    obj = build_symbol_index("sample", ["a", "b"], ["evidence"])
    assert valid_symbol_index(obj); print("[PASS] symbol index built")
    assert obj.symbols == ("a", "b") and obj.evidence == ("evidence",); print("[PASS] contract data preserved")
    assert obj.digest and valid_symbol_index(obj); print("[PASS] digest validates")
    bad = obj.to_dict(); bad["symbols"] = ["tampered"]
    assert not valid_symbol_index(SymbolIndex(obj.name, tuple(bad["symbols"]), obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.02 tests complete.")

if __name__ == "__main__":
    main()
