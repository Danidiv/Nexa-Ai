from services.completion_browser_tabs import *
def main():
 r=register_tabs([{'tab_id':'a','url':'http://localhost:1'},{'tab_id':'b','url':'http://localhost:2'}],'b');assert r.valid() and r.active_tab=='b';assert activate(r,'a').active_tab=='a';assert activate(r,'x') is None;print("="*60);print("AZIZ AI SETUP 5.12 TEST");print("="*60);[print('[PASS] '+x) for x in ['tabs tracked','active target switches','unknown tab rejected','registry digest validates']];print('\nSetup 5.12 tests complete.')
if __name__=='__main__':main()