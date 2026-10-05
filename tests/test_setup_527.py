from services.completion_visual_regression import *
def main():
 r=regression_suite([{'url':'/','baseline':'a','current':'a'},{'url':'/about','baseline':'b','current':'b'}]); assert r['status']=='pass' and valid_regression(r); b=dict(r); b['digest']='bad'; assert not valid_regression(b); print('[PASS] multi-page suite built'); print('[PASS] matching pages pass'); print('[PASS] digest validates'); print('[PASS] tamper rejected')
if __name__=='__main__': main()
