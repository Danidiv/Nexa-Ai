from pathlib import Path
from services.completion_runtime_intelligence_integration import runtime_intelligence_report,validate_runtime_report

def main():
 d=Path('tests/.tmp496'); d.mkdir(exist_ok=True); (d/'package.json').write_text('{"scripts":{"dev":"vite","build":"vite build","test":"vitest"},"dependencies":{"react":"1"}}'); (d/'.env.example').write_text('API_URL=x\n'); (d/'src').mkdir(exist_ok=True); (d/'src/main.tsx').write_text('x')
 r=runtime_intelligence_report(str(d)); assert r['status']=='ready' and validate_runtime_report(r); tam=dict(r);tam['digest']='bad';assert not validate_runtime_report(tam); tam=dict(r);tam['profile']=dict(r['profile']);tam['profile']['runtime_family']='python';assert not validate_runtime_report(tam); print('='*60);print('AZIZ AI SETUP 4.96 TEST');print('='*60);[print('[PASS] '+x) for x in ['integrated runtime intelligence validates','tampered digest rejected','tampered runtime payload rejected']];print('\nSetup 4.96 tests complete.')
if __name__=='__main__':main()
