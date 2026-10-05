from services.completion_ui_state_plan import build_ui_state_plan, valid_ui_state_plan

def main():
    obj=build_ui_state_plan("sample", **{f: [f"sample-{f}"] for f in ['loading', 'empty', 'error']})
    assert valid_ui_state_plan(obj)
    assert obj.kind == "ui_state_plan"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.17 UI State Implementation Plan")

if __name__=="__main__": main()
