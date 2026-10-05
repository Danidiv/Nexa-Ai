from services.completion_layout_intelligence import *
def main():
 r=inspect_layout('<div id="app"></div><button class="go">Go</button>'); assert valid_layout(r) and len(r['elements'])==2; b=dict(r); b['digest']='bad'; assert not valid_layout(b); print('[PASS] layout model built'); print('[PASS] selectors mapped'); print('[PASS] digest validates'); print('[PASS] tamper rejected')
if __name__=='__main__': main()
