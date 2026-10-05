"""AZIZ AI SETUP 4.14 TEST
Persistent session recovery and state persistence.
"""
import json
import os
import tempfile

from core.agent import memory
from core.agent.agent_loop import AgentSession, _safe_state_snapshot


def main():
    print("=" * 60)
    print("AZIZ AI SETUP 4.14 TEST")
    print("=" * 60)

    old_path, old_dir = memory.DATABASE_PATH, memory.DATABASE_DIR
    try:
        with tempfile.TemporaryDirectory() as tmp:
            memory.DATABASE_PATH = os.path.join(tmp, "aziz_memory.db")
            memory.DATABASE_DIR = tmp

            first = AgentSession()
            first.start_task("Create setup_414.txt containing Setup 4.14 works")
            first.state.phase = "VERIFY"
            first.state.step = 5
            first.state.verification_requested = True
            cid = first.conversation_id

            # Simulate a running session that has not completed.
            first.pending_question = "Which exact content should I use?"
            first.waiting_for_user = True
            memory.update_conversation(
                cid,
                status="active",
                pending_question=first.pending_question,
                agent_state=_safe_state_snapshot(first.state),
            )

            second = AgentSession()
            ok, data = second.recover_last_active()
            assert ok is True
            assert data["id"] == cid
            assert second.original_task == "Create setup_414.txt containing Setup 4.14 works"
            print("[PASS] most recent active conversation auto-recovery works")

            assert second.waiting_for_user is True
            assert second.pending_question == "Which exact content should I use?"
            print("[PASS] pending ask_user state survives recovery")

            assert second.state.phase == "VERIFY"
            assert second.state.step == 5
            assert second.state.verification_requested is True
            print("[PASS] agent state survives recovery")

            assert any(m["role"] == "user" for m in second.messages)
            print("[PASS] transcript context survives recovery")

            # Completed conversations must not be recovered automatically.
            memory.update_conversation(cid, status="completed", pending_question=None)
            third = AgentSession()
            ok2, msg = third.recover_last_active()
            assert ok2 is False
            print("[PASS] completed conversations are not auto-recovered")

            # State snapshot remains JSON serializable.
            json.dumps(_safe_state_snapshot(second.state))
            print("[PASS] recovered state remains JSON serializable")

    finally:
        memory.DATABASE_PATH, memory.DATABASE_DIR = old_path, old_dir

    print("\nSetup 4.14 tests complete.")


if __name__ == "__main__":
    main()
