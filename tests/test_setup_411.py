import os
import tempfile


def test_setup_411():
    from core.agent import memory
    from core.agent.agent_loop import AgentSession

    old_path = memory.DATABASE_PATH
    old_dir = memory.DATABASE_DIR
    try:
        with tempfile.TemporaryDirectory() as tmp:
            memory.DATABASE_PATH = os.path.join(tmp, "aziz_memory.db")
            memory.DATABASE_DIR = tmp

            first = AgentSession()
            first.start_task("Create setup_411.txt containing Setup 4.11 works")
            cid = first.conversation_id

            memory.add_message(cid, "assistant", '{"action":"write_file","arguments":{"path":"setup_411.txt","content":"Setup 4.11 works"}}')
            memory.add_message(cid, "user", "TOOL RESULT: SUCCESS: file written")
            memory.add_action(cid, "write_file", {"path":"setup_411.txt","content":"Setup 4.11 works"}, "SUCCESS: file written", True)
            memory.update_conversation(cid, status="completed", pending_question=None)

            short = cid[:8]
            second = AgentSession()
            ok, data = second.resume_task(short)

            assert ok is True
            assert data["id"] == cid
            assert second.conversation_id == cid
            assert second.original_task == "Create setup_411.txt containing Setup 4.11 works"
            assert any("SUCCESS: file written" in m["content"] for m in second.messages)

            # Verify pending ask_user state survives a restart.
            third = AgentSession()
            third.start_task("Create something, but ask if unclear")
            qid = third.conversation_id
            memory.add_message(qid, "assistant", '{"action":"ask_user","arguments":{"question":"Which content?"}}')
            memory.update_conversation(qid, status="active", pending_question="Which content?")

            fourth = AgentSession()
            ok2, _ = fourth.resume_task(qid[:8])
            assert ok2 is True
            assert fourth.waiting_for_user is True
            assert fourth.pending_question == "Which content?"

    finally:
        memory.DATABASE_PATH = old_path
        memory.DATABASE_DIR = old_dir


if __name__ == "__main__":
    test_setup_411()
    print("============================================================")
    print("AZIZ AI SETUP 4.11 TEST")
    print("============================================================")
    print("[PASS] short conversation ID resolves")
    print("[PASS] full transcript context restores")
    print("[PASS] pending ask_user state restores")
    print("[PASS] conversation lifecycle remains persistent")
    print("\nSetup 4.11 tests complete.")
