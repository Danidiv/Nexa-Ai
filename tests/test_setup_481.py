from services.completion_terminal_hardening import build_report,validate_report
def main():
 r=build_report(ledger_valid=True,snapshot_valid=True,replay_valid=True,recovery_valid=True); assert r["status"]=="hardened" and validate_report(r)
 r=build_report(ledger_valid=True,snapshot_valid=True,replay_valid=True,recovery_valid=False); assert r["status"]=="blocked" and validate_report(r)
 t=dict(r); t["checks"]=dict(r["checks"]); t["checks"]["recovery"]=True; assert not validate_report(t)
 r=build_report(ledger_valid=True,snapshot_valid=True,replay_valid=True,recovery_valid=True,epoch_aligned=False); assert r["status"]=="blocked"
 print("="*60); print("AZIZ AI SETUP 4.81 TEST"); print("="*60); [print("[PASS] "+x) for x in ["all terminal layers harden","failed recovery blocks","tampered report digest is rejected","epoch drift blocks hardening"]]; print("\nSetup 4.81 tests complete.")
if __name__=="__main__":main()
