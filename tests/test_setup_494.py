from pathlib import Path
from services.completion_runtime_intelligence import build_runtime_profile
from services.completion_runtime_environment import build_environment_map,RuntimeEnvironment

def main():
 d=Path('tests/.tmp494'); d.mkdir(exist_ok=True); (d/'package.json').write_text('{"dependencies":{"react":"1"},"scripts":{"dev":"vite"}}'); (d/'.env.example').write_text('API_URL=x\nPORT=3000\n'); p=build_runtime_profile(str(d)); e=build_environment_map(str(d),p); assert 'react' in e.dependency_names; assert 'API_URL' in e.environment_keys; assert e.services[0]['port']==3000; assert RuntimeEnvironment.from_dict(e.to_dict()).valid(); print('='*60);print('AZIZ AI SETUP 4.94 TEST');print('='*60);[print('[PASS] '+x) for x in ['runtime dependencies mapped','environment keys mapped','runtime services mapped','serialization and digest validate']];print('\nSetup 4.94 tests complete.')
if __name__=='__main__':main()
