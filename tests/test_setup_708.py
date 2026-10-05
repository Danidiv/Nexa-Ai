from services.completion_data_model import build_data_model, valid_data_model

def main():
    obj=build_data_model("sample", **{f: [f"sample-{f}"] for f in ['entities', 'relations', 'constraints']})
    assert valid_data_model(obj)
    assert obj.kind == "data_model"
    assert obj.task_id == "sample"
    assert obj.valid()
    print("[PASS] Setup 7.08 Data Model Mapping")

if __name__=="__main__": main()
