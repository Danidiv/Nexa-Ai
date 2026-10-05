from services.completion_performance_optimization_plan import build_performance_optimization_plan, valid_performance_optimization_plan, PerformanceOptimizationPlan

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.35 TEST")
    print("============================================================")
    obj=build_performance_optimization_plan(["a","b"], ["a","b"], ["a","b"], ["a","b"])
    assert valid_performance_optimization_plan(obj); print("[PASS] performance optimization plan built")
    assert obj.digest; print("[PASS] contract data preserved")
    assert valid_performance_optimization_plan(obj); print("[PASS] digest validates")
    assert not valid_performance_optimization_plan(PerformanceOptimizationPlan(( "tampered", ), obj.budgets, obj.actions, obj.evidence, obj.digest)); print("[PASS] tamper rejected")
    print("Setup 6.35 tests complete.")
if __name__ == "__main__": main()
