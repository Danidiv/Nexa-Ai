from services.completion_command_preflight import build_command_preflight, valid_command_preflight

def main():
    obj=build_command_preflight("sample", **{f: [f"sample-{f}"] for f in ['commands', 'scope', 'expected']})
    assert valid_command_preflight(obj)
    assert obj.kind == "command_preflight"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.23 Command Preflight")

if __name__=="__main__": main()
