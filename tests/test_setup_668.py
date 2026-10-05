from services.completion_repair_loop_controller import build_repair_loop_controller, valid_repair_loop_controller, RepairLoopController

def main():
    print("="*60); print("AZIZ AI SETUP 6.68 TEST"); print("="*60)
    obj=build_repair_loop_controller("sample", ["item-a","item-b"], ["evidence-a"])
    assert valid_repair_loop_controller(obj); print("[PASS] repair loop controller built")
    assert obj.items and obj.evidence; print("[PASS] contract data preserved")
    assert valid_repair_loop_controller(obj); print("[PASS] digest validates")
    tampered=RepairLoopController("tampered", obj.items, obj.evidence, obj.digest)
    assert not valid_repair_loop_controller(tampered); print("[PASS] tamper rejected")
    print("Setup 6.68 tests complete.")

if __name__=="__main__": main()
