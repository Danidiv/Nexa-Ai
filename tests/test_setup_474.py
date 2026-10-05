from services.completion_crash_recovery import classify_crash
def main():
 assert classify_crash("EMITTING","pending").status=="resume"; assert classify_crash("EMITTING","orphaned").status=="quarantine"; assert classify_crash("DONE","none").status=="clear"; print("="*60); print("AZIZ AI SETUP 4.74 TEST"); print("="*60); [print("[PASS] "+s) for s in ["pending crash resumes verification","orphaned crash quarantines","done crash clears"]]; print("\nSetup 4.74 tests complete.")
if __name__=="__main__":main()
