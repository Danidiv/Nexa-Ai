from services.completion_codebase_hardening import build_intelligence_contract,validate_intelligence_contract
class X:
 def __init__(self,d):self.digest=d
class P:
 def to_dict(self):return {'targets':['a.py']}
class S:
 def __init__(self,d):self.digest=d

def main():
 c=build_intelligence_contract(X('i'),[{'path':'a.py'}],X('g'),P(),S('s'),S('r'),S('c'),S('e'));assert validate_intelligence_contract(c);t=dict(c);t['digest']='bad';assert not validate_intelligence_contract(t);t=dict(c);t['payload']=dict(c['payload']);t['payload']['symbol_digest']='tampered';assert not validate_intelligence_contract(t);print('='*60);print('AZIZ AI SETUP 4.91 TEST');print('='*60);[print('[PASS] '+z) for z in ['integrated contract validates','tampered digest rejected','tampered payload rejected']];print('\nSetup 4.91 tests complete.')
if __name__=='__main__':main()
