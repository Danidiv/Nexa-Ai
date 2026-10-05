from services.completion_execution_plan import build_execution_plan, valid_execution_plan

def main():
    obj=build_execution_plan("sample", **{f: [f"sample-{f}"] for f in ['steps', 'commands', 'gates']})
    assert valid_execution_plan(obj)
    assert obj.kind == "execution_plan"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.21 Execution Plan")

if __name__=="__main__": main()
