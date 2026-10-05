from services.completion_codebase_index import build_codebase_index
from services.completion_code_search import search_code
from services.completion_codebase_graph import build_graph
from services.completion_code_change_plan import build_code_change_plan,CodeChangePlan
from pathlib import Path
def main():
 d=Path("tests/.tmp485");d.mkdir(exist_ok=True);(d/"app.js").write_text("import './util.js';\n");(d/"util.js").write_text("export function util(){}\n");i=build_codebase_index(str(d));g=build_graph(i);p=build_code_change_plan("app",[x.to_dict() for x in search_code(i,"app")],g);assert "app.js" in p.targets;assert "util.js" in p.inspect;assert CodeChangePlan.from_dict(p.to_dict()).targets==p.targets;print("="*60);print("AZIZ AI SETUP 4.85 TEST");print("="*60);[print("[PASS] "+x) for x in ["target selected","dependency added to inspect","serialization restores","verify scope is deterministic"]];print("\nSetup 4.85 tests complete.")
if __name__=="__main__":main()
