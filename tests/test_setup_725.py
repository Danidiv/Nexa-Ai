from services.completion_dependency_install import build_dependency_install, valid_dependency_install

def main():
    obj=build_dependency_install("sample", **{f: [f"sample-{f}"] for f in ['packages', 'manager', 'lockfile']})
    assert valid_dependency_install(obj)
    assert obj.kind == "dependency_install"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.25 Dependency Installation Plan")

if __name__=="__main__": main()
