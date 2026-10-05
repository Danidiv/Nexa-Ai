from services.completion_browser_inspection import inspect_html,PageInspection
def main():
 r=inspect_html("<html><head><title>Login</title></head><body><form><input type=email><button>Login</button></form><a href=/home>Home</a></body></html>","http://localhost:3000");assert r.title=="Login" and r.forms==1 and r.links==1 and r.buttons==1 and r.valid();assert PageInspection.from_dict(r.to_dict()).valid();print("="*60);print("AZIZ AI SETUP 4.99 TEST");print("="*60);[print("[PASS] "+x) for x in ["HTML page inspected","title and controls detected","serialization restores","inspection digest validates"]];print("\nSetup 4.99 tests complete.")
if __name__=="__main__":main()
