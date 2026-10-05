from pathlib import Path
from services.completion_codebase_index import build_codebase_index
from services.completion_symbol_intelligence import build_symbol_index
from services.completion_reference_analysis import build_reference_index,ReferenceIndex,references_for_path

def main():
 d=Path('tests/.tmp488');d.mkdir(exist_ok=True);(d/'base.py').write_text('class User: pass\n');(d/'use.py').write_text('from base import User\nx=User()\n');i=build_codebase_index(str(d));s=build_symbol_index(i);r=build_reference_index(i,s);assert any(x['symbol']=='User' for x in r.references);assert references_for_path(r,'use.py');assert ReferenceIndex.from_dict(r.to_dict()).digest==r.digest;print('='*60);print('AZIZ AI SETUP 4.88 TEST');print('='*60);[print('[PASS] '+x) for x in ['cross-file reference detected','path references are queryable','serialization restores','reference digest is deterministic']];print('\nSetup 4.88 tests complete.')
if __name__=='__main__':main()
