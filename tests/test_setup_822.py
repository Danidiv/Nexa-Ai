from services.phase8_822_development_server_manager import build_822, valid_822

def main():
    obj=build_822("sample", goal="build product", items=["a","a","b"], risk="low")
    assert valid_822(obj)
    assert obj.setup=="8.22"
    assert obj.kind=="Development Server Manager"
    assert obj.valid()
    bad=type(obj)(obj.setup,obj.task_id,obj.kind,obj.payload,"tampered")
    assert not valid_822(bad)
    try: build_822("")
    except ValueError: pass
    else: raise AssertionError("empty task_id must be rejected")
    print("[PASS] Setup 8.22 Development Server Manager")

if __name__=="__main__": main()
