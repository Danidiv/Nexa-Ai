from services.completion_terminal_state_machine import TerminalStateMachine
def main():
 m=TerminalStateMachine(); assert m.transition("VERIFYING"); assert m.transition("RESOLVING"); assert m.transition("AUTHORIZED"); assert m.transition("EMITTING"); assert m.transition("AUDITED"); assert m.transition("DONE"); assert m.can_finalize(); assert not m.transition("IDLE"); x=TerminalStateMachine.from_dict(m.to_dict()); assert x and x.sequence==m.sequence; print("="*60); print("AZIZ AI SETUP 4.72 TEST"); print("="*60); [print("[PASS] "+s) for s in ["valid lifecycle","monotonic sequence","terminal DONE boundary","illegal transition rejected","serialization and restore"]]; print("\nSetup 4.72 tests complete.")
if __name__=="__main__":main()
