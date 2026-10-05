from services.completion_codebase_index import build_codebase_index
from services.completion_code_search import search_code
from pathlib import Path
def main():
 d=Path("tests/.tmp483");d.mkdir(exist_ok=True);(d/"auth.py").write_text("def login_user(): pass\n");(d/"cart.py").write_text("def add_item(): pass\n")
 i=build_codebase_index(str(d));r=search_code(i,"login");assert r and r[0].path=="auth.py";assert search_code(i,"no_such_term")==[];assert r[0].score>0;print("="*60);print("AZIZ AI SETUP 4.83 TEST");print("="*60);[print("[PASS] "+x) for x in ["relevant search ranks first","unknown search returns empty","results are scored"]];print("\nSetup 4.83 tests complete.")
if __name__=="__main__":main()
