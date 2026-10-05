from pathlib import Path
from services.completion_codebase_index import build_codebase_index
from services.completion_symbol_intelligence import build_symbol_index,SymbolIndex

def main():
 d=Path('tests/.tmp487');d.mkdir(exist_ok=True);(d/'a.py').write_text('class User:\n    def save(self): pass\n')
 i=build_codebase_index(str(d)); s=build_symbol_index(i); assert any(x['name']=='User' and x['kind']=='class' for x in s.symbols); assert any(x['name']=='save' and x['kind']=='function' for x in s.symbols); assert SymbolIndex.from_dict(s.to_dict()).digest==s.digest; print('='*60);print('AZIZ AI SETUP 4.87 TEST');print('='*60);[print('[PASS] '+x) for x in ['symbol records are built','class and function symbols detected','serialization restores','symbol digest is deterministic']];print('\nSetup 4.87 tests complete.')
if __name__=='__main__':main()
