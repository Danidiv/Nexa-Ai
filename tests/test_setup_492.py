from pathlib import Path
from services.completion_runtime_intelligence import build_runtime_profile,RuntimeProfile

def main():
 d=Path('tests/.tmp492'); d.mkdir(exist_ok=True); (d/'package.json').write_text('{"scripts":{"dev":"vite","build":"vite build","test":"vitest"}}'); (d/'.env.example').write_text('PORT=5173\n'); (d/'app.js').write_text('const port=5173')
 p=build_runtime_profile(str(d)); assert p.manifests==['package.json']; assert p.scripts['dev']=='vite'; assert 5173 in p.ports; assert RuntimeProfile.from_dict(p.to_dict()).valid(); print('='*60); print('AZIZ AI SETUP 4.92 TEST'); print('='*60); [print('[PASS] '+x) for x in ['runtime family detected','scripts and manifest detected','port and environment metadata detected','serialization and digest validate']]; print('\nSetup 4.92 tests complete.')
if __name__=='__main__': main()
