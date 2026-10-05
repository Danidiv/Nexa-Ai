from services.completion_browser_automation import create_session

def main():
 s=create_session('t','http://localhost:5173'); assert s.policy.allows(s.target.url); s.actions.append({'action':'navigate','url':s.target.url}); s.seal(); assert s.valid(); d=s.to_dict(); assert s.from_dict(d).valid()
 print('='*60);print('AZIZ AI SETUP 5.02 TEST');print('='*60)
 for x in ['session created','safety policy enforced','serialization restores','session digest validates']:print('[PASS] '+x)
 print('\nSetup 5.02 tests complete.')
if __name__=='__main__':main()
