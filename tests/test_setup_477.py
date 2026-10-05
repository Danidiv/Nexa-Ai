from services.completion_transition_ledger import TransitionLedger
def main():
 l=TransitionLedger(); l.append("IDLE","VERIFYING"); l.append("VERIFYING","RESOLVING"); assert l.valid(); assert l.head_digest
 assert len(TransitionLedger.from_dict(l.to_dict()).entries)==2
 t=l.to_dict(); t["entries"][0]["target"]="DONE"; assert TransitionLedger.from_dict(t) is None
 for i in range(100): l.append("A","B",str(i))
 assert len(l.entries)==64 and l.valid()
 print("="*60); print("AZIZ AI SETUP 4.77 TEST"); print("="*60); [print("[PASS] "+s) for s in ["ledger appends and seals","serialization restores valid ledger","tamper is rejected","history remains bounded"]]; print("\nSetup 4.77 tests complete.")
if __name__=="__main__":main()
