from services.completion_change_transaction import build_change_transaction, valid_change_transaction

def main():
    obj=build_change_transaction("sample", **{f: [f"sample-{f}"] for f in ['files', 'commit_points', 'rollback']})
    assert valid_change_transaction(obj)
    assert obj.kind == "change_transaction"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.24 Change Transaction Plan")

if __name__=="__main__": main()
