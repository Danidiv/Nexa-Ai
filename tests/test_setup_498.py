from services.completion_live_preview import LivePreview,PreviewState
def main():
 p=LivePreview(["python","-c","import time; time.sleep(0.2)"],"http://localhost:1");assert p.state.status=="not_started" and p.state.valid();assert p.start();assert p.healthy();p.stop();assert p.state.status=="stopped" and p.state.valid();print("="*60);print("AZIZ AI SETUP 4.98 TEST");print("="*60);[print("[PASS] "+x) for x in ["preview starts","running state is healthy","preview stops safely","state digest validates"]];print("\nSetup 4.98 tests complete.")
if __name__=="__main__":main()
