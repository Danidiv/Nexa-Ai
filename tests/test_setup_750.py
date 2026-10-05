from services.completion_lovable_level_builder import build_lovable_level_builder, valid_lovable_level_builder, LovableLevelBuilder

def main():
    obj=build_lovable_level_builder("sample", "build a customer dashboard", ["understood","implemented","tested"], "verified")
    assert valid_lovable_level_builder(obj)
    assert obj.phases == ("UNDERSTAND","IMPLEMENT","EXECUTE","VERIFY","REPAIR","RELEASE")
    assert obj.status == "verified"
    tampered=LovableLevelBuilder(obj.task_id,obj.request,obj.phases,obj.evidence,"blocked",obj.digest_value)
    assert not valid_lovable_level_builder(tampered)
    print("[PASS] Setup 7.50 Lovable-Level Product Builder V1")

if __name__=="__main__": main()
