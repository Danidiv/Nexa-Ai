"""AZIZ AI SETUP 4.28 TEST - bounded secret-safe gateway event stream."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from core.models.lm_studio import LMStudioGateway


def response(content="ok"):
    r = Mock(); r.status_code = 200; r.raise_for_status.return_value = None
    r.json.return_value = {"choices": [{"message": {"content": content}}]}
    return r


def main():
    print("=" * 60); print("AZIZ AI SETUP 4.28 TEST"); print("=" * 60)
    with TemporaryDirectory() as td:
        event_path = Path(td) / "events.jsonl"
        g = LMStudioGateway(max_retries=0, event_log_limit=5, event_log_path=str(event_path))
        with patch("core.models.lm_studio.requests.post", return_value=response("ok")):
            assert g.chat([{"role": "user", "content": "TOP SECRET PROMPT"}]) == "ok"
        events = g.events
        assert any(e["event"] == "request_started" for e in events)
        assert any(e["event"] == "request_completed" for e in events)
        raw = "\n".join(str(e) for e in events)
        assert "TOP SECRET PROMPT" not in raw and "choices" not in raw
        print("[PASS] request lifecycle events are recorded without request payloads")

        g._events.record("custom", request_id="safe", secret="DO NOT STORE", prompt="DO NOT STORE")
        assert all("secret" not in e and "prompt" not in e for e in g.events)
        print("[PASS] event fields are whitelist-filtered")

        saved = g.save_event_log()
        assert Path(saved).exists()
        text = Path(saved).read_text(encoding="utf-8")
        assert "TOP SECRET PROMPT" not in text and "DO NOT STORE" not in text
        print("[PASS] event log persists as safe JSONL")

        restored = LMStudioGateway(max_retries=0, event_log_limit=5, event_log_path=str(event_path))
        assert restored.load_event_log() == len(g.events)
        assert restored.events == g.events
        print("[PASS] persisted event log restores bounded event history")

        for i in range(10):
            g._events.record("test_event", request_id=str(i))
        assert len(g.events) == 5
        print("[PASS] event stream remains bounded")

    print("\nSetup 4.28 tests complete.")


if __name__ == "__main__":
    main()
