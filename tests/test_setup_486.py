from services.completion_codebase_intelligence import intelligence_report,validate_report
from pathlib import Path
def main():
 d=Path("tests/.tmp486");d.mkdir(exist_ok=True);(d/"main.py").write_text("def main(): pass\n")
 r=intelligence_report(str(d),"main");assert r["status"]=="ready" and validate_report(r);tam=dict(r);tam["digest"]="bad";assert not validate_report(tam);tam=dict(r);tam["plan"]=dict(r["plan"]);tam["plan"]["targets"]=list(r["plan"]["targets"])+["evil.py"];assert not validate_report(tam);print("="*60);print("AZIZ AI SETUP 4.86 TEST");print("="*60);[print("[PASS] "+x) for x in ["integrated intelligence report validates","tampered digest rejected","tampered plan rejected"]];print("\nSetup 4.86 tests complete.")
if __name__=="__main__":main()
