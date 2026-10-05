from services.completion_change_selection import select_change_targets
from services.completion_multi_file_execution import build_execution_plan,MultiFileExecutionPlan
class G: pass

def main():
 sel=select_change_targets('User',[{'path':'api.py','score':3}],type('S',(),{'symbols':[]})(),type('R',(),{'references':[]})()); cp=type('P',(),{'inspect':['models.py'],'verify':['api.py'],'change':['api.py']})();e=build_execution_plan(sel,cp);assert [x['name'] for x in e.stages]==['inspect','change','verify'];assert e.stages[1]['paths']==['api.py'];assert MultiFileExecutionPlan.from_dict(e.to_dict()).digest==e.digest;print('='*60);print('AZIZ AI SETUP 4.90 TEST');print('='*60);[print('[PASS] '+z) for z in ['inspect stage precedes change','change stage targets selected files','verify stage is present','serialization restores']];print('\nSetup 4.90 tests complete.')
if __name__=='__main__':main()
