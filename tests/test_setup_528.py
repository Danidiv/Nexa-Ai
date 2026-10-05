from services.completion_browser_flow_suite import *
def main():
 r=build_flow_suite([{'action':'navigate','target':'/login','expected':'login'},{'action':'click','target':'#submit','expected':'dashboard'}]); assert valid_flow_suite(r) and len(r['steps'])==2; b=dict(r); b['digest']='bad'; assert not valid_flow_suite(b); print('[PASS] flow suite built'); print('[PASS] steps normalized'); print('[PASS] digest validates'); print('[PASS] tamper rejected')
if __name__=='__main__': main()
