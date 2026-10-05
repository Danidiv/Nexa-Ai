from services.completion_database_plan import build_database_plan, valid_database_plan

def main():
    obj=build_database_plan("sample", **{f: [f"sample-{f}"] for f in ['tables', 'migrations', 'indexes']})
    assert valid_database_plan(obj)
    assert obj.kind == "database_plan"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.14 Database Implementation Plan")

if __name__=="__main__": main()
