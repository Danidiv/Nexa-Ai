from services.phase8_900_integrated_product_builder_v4 import build_900,valid_900
def main():
 o=build_900("sample",product={"goal":"saas"},implementation={"plan":{"nodes":["ui","api","db"],"edges":[["ui","api"],["api","db"]]}},release={"status":"ready"},operations={"health":"ok"},feedback={"count":1},security={"status":"passed"})
 assert valid_900(o) and o.valid()
 t=type(o)(o.setup,o.task_id,o.kind,{**o.payload,"risk":"critical"},o.digest_value)
 assert not valid_900(t)
 print("[PASS] Setup 9.00 Integrated Lovable-Level Product Builder V4")
if __name__=="__main__": main()
