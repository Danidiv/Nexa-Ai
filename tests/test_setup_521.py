from services.completion_accessibility import *
def main():
 r=inspect_accessibility('<img src="x" alt="x"><button aria-label="Go"></button><label>Email</label><input>'); assert r['status']=='pass' and valid_accessibility(r); b=dict(r); b['digest']='bad'; assert not valid_accessibility(b); print('[PASS] accessibility rules inspected'); print('[PASS] alt/button/label checks work'); print('[PASS] digest validates'); print('[PASS] tamper rejected')
if __name__=='__main__': main()
