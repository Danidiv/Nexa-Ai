from services.completion_codebase_index import build_codebase_index
from services.completion_codebase_graph import build_graph,CodebaseGraph
from pathlib import Path
def main():
 d=Path("tests/.tmp484");d.mkdir(exist_ok=True);(d/"a.js").write_text("import x from './x.js';\n");(d/"x.js").write_text("export const x=1;\n")
 g=build_graph(build_codebase_index(str(d)));assert g.edges["a.js"]==["x.js"];assert g.reverse["x.js"]==["a.js"];assert CodebaseGraph.from_dict(g.to_dict()).digest==g.digest;assert g.nodes==sorted(g.nodes);print("="*60);print("AZIZ AI SETUP 4.84 TEST");print("="*60);[print("[PASS] "+x) for x in ["dependency edge resolved","reverse edge resolved","serialization restores","graph nodes deterministic"]];print("\nSetup 4.84 tests complete.")
if __name__=="__main__":main()
