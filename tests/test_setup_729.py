from services.completion_long_task_checkpoint import build_long_task_checkpoint, valid_long_task_checkpoint

def main():
    obj=build_long_task_checkpoint("sample", **{f: [f"sample-{f}"] for f in ['checkpoint', 'resume', 'state']})
    assert valid_long_task_checkpoint(obj)
    assert obj.kind == "long_task_checkpoint"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.29 Long Task Checkpoint")

if __name__=="__main__": main()
