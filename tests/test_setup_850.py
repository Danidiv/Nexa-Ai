from services.phase8_850_integrated_product_builder_v3 import build_850, valid_850

def main():
    obj=build_850("sample", requirements={"goal":"build SaaS"}, architecture={"frontend":"react","backend":"api"}, plan={"nodes":["ui","api","db"],"edges":[["ui","api"],["api","db"]]}, qa={"status":"passed"}, evidence=["build","test","verify"], risk="low")
    assert valid_850(obj)
    assert obj.valid()
    tampered=type(obj)(obj.setup,obj.task_id,obj.kind,{**obj.payload,"risk":"critical"},obj.digest_value)
    assert not valid_850(tampered)
    print("[PASS] Setup 8.50 Integrated Lovable-Level Product Builder V3")
if __name__=="__main__": main()
