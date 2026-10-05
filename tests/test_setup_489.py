from services.completion_change_selection import select_change_targets,ChangeSelection
class G: pass

def main():
 g=G();s=type('S',(),{'symbols':[{'name':'User','path':'models.py'},{'name':'save','path':'models.py'}]})();r=type('R',(),{'references':[{'source':'api.py','symbol':'User','target':'models.py'}]})();x=select_change_targets('User',[{'path':'api.py','score':4}],s,r);assert x.targets[0]=='api.py';assert 'models.py' in x.targets;assert ChangeSelection.from_dict(x.to_dict()).digest==x.digest;tam=x.to_dict();tam['targets']=['evil.py'];assert not ChangeSelection.from_dict(tam).valid();print('='*60);print('AZIZ AI SETUP 4.89 TEST');print('='*60);[print('[PASS] '+z) for z in ['direct target selected','related symbol target added','serialization restores','tampered selection changes digest']];print('\nSetup 4.89 tests complete.')
if __name__=='__main__':main()
