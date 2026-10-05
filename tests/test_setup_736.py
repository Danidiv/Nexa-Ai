from services.completion_api_browser import build_api_browser, valid_api_browser

def main():
    obj=build_api_browser("sample", **{f: [f"sample-{f}"] for f in ['requests', 'responses', 'errors']})
    assert valid_api_browser(obj)
    assert obj.kind == "api_browser"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.36 API Browser Verification")

if __name__=="__main__": main()
