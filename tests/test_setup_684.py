from services.completion_implementation_context import build_implementation_context, valid_implementation_context, ImplementationContext

def main():
    print("="*60); print("AZIZ AI SETUP 6.84 TEST"); print("="*60)
    obj=build_implementation_context('sample', ['app.py'], ['login'], ['def login():'])
    assert valid_implementation_context(obj); print("[PASS] implementation context selection built")
    assert bool(obj.task_id) and bool(obj.files) and bool(obj.symbols) and bool(obj.snippets); print("[PASS] contract data preserved")
    assert valid_implementation_context(obj); print("[PASS] digest validates")
    tampered=ImplementationContext("tampered", obj.files, obj.symbols, obj.snippets, obj.digest)
    assert not valid_implementation_context(tampered); print("[PASS] tamper rejected")
    print("Setup 6.84 tests complete.")

if __name__=="__main__": main()
