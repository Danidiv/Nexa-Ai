from services.phase10_integrated_lovable_level_product_builder_v6 import build_1000, valid_1000

def main():
    o=build_1000("sample",nodes=["understand","plan","build","test","verify"],edges=[["understand","plan"],["plan","build"],["build","test"],["test","verify"]],criteria=["login","crud"],config={"DATABASE_URL":"postgres://x","API_TOKEN":"secret"})
    assert valid_1000(o) and o.valid() and o.setup=="10.00"
    assert o.payload["session"]["order"]==["understand","plan","build","test","verify"]
    assert o.payload["session"]["config"]["API_TOKEN"]=="***REDACTED***"
    assert o.payload["session"]["status"]=="verified"
    bad=type(o)(o.setup,o.task_id,o.kind,o.payload,"tampered")
    assert not valid_1000(bad)
    print("[PASS] Setup 10.00 Integrated Lovable-Level Product Builder V6")

if __name__=="__main__": main()
