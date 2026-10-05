from pathlib import Path
from services.completion_runtime_intelligence import build_runtime_profile
from services.completion_runtime_entrypoints import discover_entrypoints,EntryPointIndex

def main():
 d=Path('tests/.tmp493'); d.mkdir(exist_ok=True); (d/'package.json').write_text('{"scripts":{"dev":"vite"}}'); (d/'src').mkdir(exist_ok=True); (d/'src/main.tsx').write_text('export default 1'); (d/'server.py').write_text('from fastapi import FastAPI\napp=FastAPI()')
 p=build_runtime_profile(str(d)); e=discover_entrypoints(str(d),p); assert any(x['path']=='src/main.tsx' for x in e.entries); assert any(x['kind']=='python-server' for x in e.entries); assert EntryPointIndex.from_dict(e.to_dict()).valid(); print('='*60);print('AZIZ AI SETUP 4.93 TEST');print('='*60);[print('[PASS] '+x) for x in ['conventional entry point detected','server entry signal detected','serialization and digest validate']];print('\nSetup 4.93 tests complete.')
if __name__=='__main__':main()
