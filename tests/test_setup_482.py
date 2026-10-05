from services.completion_codebase_index import build_codebase_index,CodebaseIndex
from pathlib import Path
def main():
 d=Path("tests/.tmp482");d.mkdir(exist_ok=True);(d/"a.py").write_text("import b\ndef hello(): pass\n");(d/"b.py").write_text("class B: pass\n")
 i=build_codebase_index(str(d));assert i.files and "hello" in i.symbols["a.py"];assert CodebaseIndex.from_dict(i.to_dict()).digest==i.digest; tam=i.to_dict();tam["digest"]="bad";assert CodebaseIndex.from_dict(tam).digest=="bad";assert len(i.files)<=120;print("="*60);print("AZIZ AI SETUP 4.82 TEST");print("="*60);[print("[PASS] "+x) for x in ["index builds metadata","symbols are indexed","serialization restores","index is bounded"]];print("\nSetup 4.82 tests complete.")
if __name__=="__main__":main()
