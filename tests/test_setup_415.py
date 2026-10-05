"""AZIZ AI SETUP 4.15 TEST - conversation lifecycle."""
import os
import tempfile
from core.agent import memory
from core.agent.agent_loop import AgentSession, _safe_state_snapshot

def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.15 TEST")
    print("=" * 60)
    old_path, old_dir = memory.DATABASE_PATH, memory.DATABASE_DIR
    try:
        with tempfile.TemporaryDirectory() as tmp:
            memory.DATABASE_PATH = os.path.join(tmp, "aziz_memory.db")
            memory.DATABASE_DIR = tmp
            s = AgentSession(); s.start_task("Lifecycle test")
            cid=s.conversation_id
            memory.set_conversation_status(cid, "running", agent_state=_safe_state_snapshot(s.state))
            assert memory.get_conversation(cid)["status"] == "running"
            print("[PASS] running lifecycle state persists")
            s.pending_question="Need clarification"; s.waiting_for_user=True
            memory.set_conversation_status(cid,"waiting_for_user",pending_question=s.pending_question,agent_state=_safe_state_snapshot(s.state))
            assert memory.get_conversation(cid)["status"] == "waiting_for_user"
            print("[PASS] waiting_for_user lifecycle state persists")
            rows=memory.recoverable_conversations()
            assert rows and rows[0]["id"]==cid
            print("[PASS] waiting conversation is recoverable")
            memory.set_conversation_status(cid,"completed",pending_question=None,agent_state=_safe_state_snapshot(s.state))
            assert not memory.recoverable_conversations()
            print("[PASS] completed conversation is excluded from recovery")
            r=AgentSession(); ok,data=r.recover_last_active(); assert ok is False
            print("[PASS] recovery does not reopen completed conversation")
            memory.set_conversation_status(cid,"active",agent_state=_safe_state_snapshot(s.state))
            r2=AgentSession(); ok2,data2=r2.recover_last_active(); assert ok2 and r2.conversation_id==cid
            print("[PASS] active conversation can be recovered")
    finally:
        memory.DATABASE_PATH, memory.DATABASE_DIR = old_path, old_dir
    print("\nSetup 4.15 tests complete.")
if __name__ == "__main__": main()
