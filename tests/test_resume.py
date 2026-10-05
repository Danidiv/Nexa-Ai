import os
import tempfile


def test_resume():
    from core.agent import memory
    from core.agent.agent_loop import AgentSession

    original_path = memory.DATABASE_PATH
    original_dir = memory.DATABASE_DIR

    try:
        with tempfile.TemporaryDirectory() as tmp:
            memory.DATABASE_PATH = os.path.join(tmp, "aziz_memory.db")
            memory.DATABASE_DIR = tmp

            first = AgentSession()
            first.start_task("Create test_410.txt containing Setup 4.10")
            real_cid = first.conversation_id
            memory.add_message(real_cid, "assistant", '{"action":"final_answer","arguments":{"answer":"done"}}')
            memory.update_conversation(real_cid, status="completed")

            second = AgentSession()
            ok, data = second.resume_task(real_cid)

            assert ok is True
            assert data["id"] == real_cid
            assert second.conversation_id == real_cid
            assert second.original_task == "Create test_410.txt containing Setup 4.10"
            assert second.messages[0]["role"] == "system"
            assert any(
                m["role"] == "user" and "Setup 4.10" in m["content"]
                for m in second.messages
            )
    finally:
        memory.DATABASE_PATH = original_path
        memory.DATABASE_DIR = original_dir


if __name__ == "__main__":
    test_resume()
    print("============================================================")
    print("AZIZ AI RESUME TEST")
    print("============================================================")
    print("[PASS] saved conversation can be resumed")
    print("[PASS] conversation ID restored")
    print("[PASS] original task restored")
    print("[PASS] model message context restored")
    print("\nSetup 4.10 resume tests complete.")
