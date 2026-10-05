from services.phase9_921_ui_page_compiler import build_921,valid_921

def main():
    o=build_921("sample",items=["a","a","b"],nodes=["ui","api","db"],edges=[["ui","api"],["api","db"]],context={"setup":"9.21","goal":"saas"},risk="low")
    assert valid_921(o) and o.valid() and o.setup=="9.21" and o.kind=="UI Page Compiler"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_921(bad)
    try: build_921("")
    except ValueError: pass
    else: raise AssertionError("empty task_id accepted")
    print("[PASS] Setup 9.21 UI Page Compiler")

if __name__=="__main__": main()
