from services.phase10_product_factory_knowledge_loop import build_998, valid_998

def main():
    o=build_998("sample", items=["a","a","b"], nodes=["ui","api","db"], edges=[["ui","api"],["api","db"]], context={"setup":"998"}, risk="low")
    assert valid_998(o) and o.valid() and o.setup=="998" and o.kind=="Product Factory Knowledge Loop"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_998(bad)
    try: build_998("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 998 Product Factory Knowledge Loop")

if __name__=="__main__": main()
