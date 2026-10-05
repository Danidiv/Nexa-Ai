from services.completion_builder_policy import build_builder_policy, valid_builder_policy

def main():
    obj=build_builder_policy("sample", **{f: [f"sample-{f}"] for f in ['permissions', 'stop_conditions', 'human_escalation']})
    assert valid_builder_policy(obj)
    assert obj.kind == "builder_policy"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.48 Product Builder Policy")

if __name__=="__main__": main()
