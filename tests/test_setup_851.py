from services.phase8_851_product_backlog_compiler import build_851,valid_851
def main():
    o=build_851("sample",goal="build product",items=["a","a","b"],risk="low",nodes=["ui","api"],edges=[["ui","api"]])
    assert valid_851(o) and o.valid() and o.setup=="8.51" and o.kind=="Product Backlog Compiler"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_851(bad)
    try: build_851("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 8.51 Product Backlog Compiler")
if __name__=="__main__": main()
