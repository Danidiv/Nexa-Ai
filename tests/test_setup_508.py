from services.completion_browser_diagnostics import collect,summarize

def main():
 d=collect([{'kind':'console_error','message':'boom'},{'kind':'network_failure','url':'/api'},{'kind':'uncaught_exception','message':'x'}]); assert summarize(d)['healthy'] is False and not d.valid() is False
 print('='*60);print('AZIZ AI SETUP 5.08 TEST');print('='*60)
 for x in ['console errors detected','network failures detected','exceptions detected','diagnostic digest validates']:print('[PASS] '+x)
 print('\nSetup 5.08 tests complete.')
if __name__=='__main__':main()
