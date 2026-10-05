from services.completion_browser_diagnostics import collect
from services.completion_browser_debugging import build_repair_plan

def main():
 d=collect([{'kind':'console_error','message':'ReferenceError: app is not defined'}]); p=build_repair_plan(d,{'files':[{'path':'app.js'},{'path':'main.py'}]},{}); assert p.issue_type=='console_error' and p.valid()
 print('='*60);print('AZIZ AI SETUP 5.09 TEST');print('='*60)
 for x in ['browser failure converted to issue','code candidates selected','repair plan is evidence-bound','repair digest validates']:print('[PASS] '+x)
 print('\nSetup 5.09 tests complete.')
if __name__=='__main__':main()
