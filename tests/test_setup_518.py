from services.completion_browser_error_localization import *
def main():
 r=localize_browser_error('login timeout in auth_service.py',[{'path':'auth_service.py','content':'def login(): timeout error'}]);assert r['candidates'] and valid_localization(r);b=dict(r);b['candidates']=[];assert not valid_localization(b);print("="*60);print("AZIZ AI SETUP 5.18 TEST");print("="*60);[print('[PASS] '+x) for x in ['browser error localized','code candidates selected','evidence reason recorded','localization digest validates']];print('\nSetup 5.18 tests complete.')
if __name__=='__main__':main()