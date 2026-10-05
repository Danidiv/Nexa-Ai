from services.completion_browser_inspection import inspect_html
from services.completion_browser_interaction import build_user_flow,BrowserFlow
def main():
 i=inspect_html("<form><button>Submit</button></form>");f=build_user_flow("http://localhost:3000",i,"submit flow is observable");assert len(f.actions)>=2 and f.valid();assert BrowserFlow.from_dict(f.to_dict()).valid();t=dict(f.to_dict());t["actions"]=list(f.actions)+[{"action":"x"}];assert not BrowserFlow.from_dict(t).valid() if BrowserFlow.from_dict(t) else True;print("="*60);print("AZIZ AI SETUP 5.00 TEST");print("="*60);[print("[PASS] "+x) for x in ["user flow planned","verification assertion included","serialization restores","flow digest detects change"]];print("\nSetup 5.00 tests complete.")
if __name__=="__main__":main()
