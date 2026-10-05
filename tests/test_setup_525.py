from services.completion_performance import *
def main():
 r=performance_report({'load_ms':1200,'dom_content_loaded_ms':500,'transfer_bytes':10000}); assert r['status']=='pass' and valid_performance(r); b=dict(r); b['metrics']={'load_ms':9999}; assert not valid_performance(b); print('[PASS] performance metrics captured'); print('[PASS] threshold status works'); print('[PASS] digest validates'); print('[PASS] tamper rejected')
if __name__=='__main__': main()
