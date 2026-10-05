import os
import tempfile
import uuid


def test_memory():
    from core.agent import memory

    original = memory.DATABASE_PATH
    original_dir = memory.DATABASE_DIR
    with tempfile.TemporaryDirectory() as tmp:
        memory.DATABASE_PATH = os.path.join(tmp, "aziz_memory.db")
        memory.DATABASE_DIR = tmp

        cid = str(uuid.uuid4())
        memory.create_conversation(cid, "Create a test file")
        memory.add_message(cid, "user", "Create a test file")
        memory.add_action(cid, "write_file", {"path": "test.txt", "content": "hello"}, "SUCCESS", True)
        memory.update_conversation(cid, status="completed")

        data = memory.get_conversation(cid)
        assert data["task"] == "Create a test file"
        assert data["status"] == "completed"
        assert len(data["messages"]) == 1
        assert len(data["actions"]) == 1
        assert data["actions"][0]["success"] == 1

        history = memory.list_conversations()
        assert any(item["id"] == cid for item in history)

    memory.DATABASE_PATH = original
    memory.DATABASE_DIR = original_dir


if __name__ == "__main__":
    test_memory()
    print("============================================================")
    print("AZIZ AI PERSISTENT MEMORY TEST")
    print("============================================================")
    print("[PASS] conversation persisted")
    print("[PASS] message persisted")
    print("[PASS] action persisted")
    print("[PASS] history retrieval works")
    print("\nSetup 4.9 memory tests complete.")
