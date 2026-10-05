from services.completion_tool_selection import build_tool_selection, valid_tool_selection

def main():
    obj=build_tool_selection("sample", **{f: [f"sample-{f}"] for f in ['step_tools', 'read_before_write', 'verification']})
    assert valid_tool_selection(obj)
    assert obj.kind == "tool_selection"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.22 Tool Selection")

if __name__=="__main__": main()
