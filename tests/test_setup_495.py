from pathlib import Path
from services.completion_runtime_intelligence import build_runtime_profile
from services.completion_runtime_entrypoints import discover_entrypoints
from services.completion_runtime_environment import build_environment_map
from services.completion_runtime_verification import build_verification_plan,RuntimeVerificationPlan

def main():
 d=Path('tests/.tmp495'); d.mkdir(exist_ok=True); (d/'package.json').write_text('{"scripts":{"build":"vite build","test":"vitest","dev":"vite"}}'); (d/'src').mkdir(exist_ok=True); (d/'src/main.tsx').write_text('x'); p=build_runtime_profile(str(d)); e=discover_entrypoints(str(d),p); env=build_environment_map(str(d),p); v=build_verification_plan(p,e,env); assert v.stages[0]['name']=='static'; assert any(s['name']=='build' for s in v.stages); assert RuntimeVerificationPlan.from_dict(v.to_dict()).valid(p,e,env); print('='*60);print('AZIZ AI SETUP 4.95 TEST');print('='*60);[print('[PASS] '+x) for x in ['static verification stage present','build and runtime verification planned','serialization and digest validate']];print('\nSetup 4.95 tests complete.')
if __name__=='__main__':main()
