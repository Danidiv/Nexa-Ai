from services.completion_accessibility import inspect_accessibility
from services.completion_accessibility_repair import *
def main():
 a=inspect_accessibility('<img src="x"><button>Go</button>'); r=build_accessibility_repair(a); assert r['actions'] and valid_accessibility_repair(r,a); b=dict(r); b['source_digest']='bad'; assert not valid_accessibility_repair(b,a); print('[PASS] repair plan built'); print('[PASS] repair is evidence-bound'); print('[PASS] digest validates'); print('[PASS] tamper rejected')
if __name__=='__main__': main()
