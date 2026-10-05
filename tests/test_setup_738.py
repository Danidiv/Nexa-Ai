from services.completion_console_verification import build_console_verification, valid_console_verification

def main():
    obj=build_console_verification("sample", **{f: [f"sample-{f}"] for f in ['errors', 'warnings', 'source']})
    assert valid_console_verification(obj)
    assert obj.kind == "console_verification"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.38 Runtime Console Verification")

if __name__=="__main__": main()
