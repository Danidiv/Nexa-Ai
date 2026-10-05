from services.completion_replay_guard import ReplayGuard,transition_id
def main():
 g=ReplayGuard(); assert g.accept(1,"IDLE","VERIFYING","start"); assert not g.accept(1,"IDLE","VERIFYING","start"); assert g.accept(2,"VERIFYING","RESOLVING","next"); assert g.valid(); assert transition_id(1,"A","B","x")==transition_id(1,"A","B","x")
 d=g.to_dict(); assert ReplayGuard.from_dict(d) is not None; d["seen"].append(d["seen"][0]); assert ReplayGuard.from_dict(d) is None
 print("="*60); print("AZIZ AI SETUP 4.79 TEST"); print("="*60); [print("[PASS] "+x) for x in ["first transition accepted","duplicate transition rejected","distinct transition accepted","serialization and deterministic identity","duplicate snapshot history rejected"]]; print("\nSetup 4.79 tests complete.")
if __name__=="__main__":main()
