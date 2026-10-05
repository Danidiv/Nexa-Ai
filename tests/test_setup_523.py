from services.completion_visual_diff import *
def main():
 r=compare_visual('a','b'); assert r['status']=='changed' and valid_visual_diff(r); assert compare_visual('a','a')['status']=='match'; b=dict(r); b['digest']='bad'; assert not valid_visual_diff(b); print('[PASS] visual change detected'); print('[PASS] visual match detected'); print('[PASS] digest validates'); print('[PASS] tamper rejected')
if __name__=='__main__': main()
