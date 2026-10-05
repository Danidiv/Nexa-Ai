"""AZIZ AI SETUP 4.29 TEST - safe startup runtime recovery."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
import json
from core.models.lm_studio import LMStudioGateway


def response(content="ok"):
    r = Mock(); r.status_code = 200; r.raise_for_status.return_value = None
    r.json.return_value = {"choices": [{"message": {"content": content}}]}
    return r


def main():
    print("=" * 60); print("AZIZ AI SETUP 4.29 TEST"); print("=" * 60)
    with TemporaryDirectory() as td:
        snap = Path(td) / "runtime.json"
        events = Path(td) / "events.jsonl"
        g = LMStudioGateway(max_retries=0, snapshot_path=str(snap), event_log_path=str(events), event_log_limit=6)
        with patch("core.models.lm_studio.requests.post", return_value=response("ok")):
            assert g.chat([{"role": "user", "content": "secret"}]) == "ok"
        g.save_snapshot(); g.save_event_log()
        original = g.export_state()

        recovered = LMStudioGateway(max_retries=0, snapshot_path=str(snap), event_log_path=str(events), event_log_limit=6)
        report = recovered.restore_runtime()
        assert report["snapshot"]["restored"]
        assert report["event_log"]["restored"]
        assert recovered.export_state()["request_history"] == original["request_history"]
        assert len(recovered.events) == len(g.events) + 1 or len(recovered.events) == 6
        print("[PASS] persisted snapshot and event log restore together")

        before = recovered.export_state()
        snap.write_text('{"snapshot_version": 999}', encoding="utf-8")
        bad = recovered.restore_runtime(snapshot_path=str(snap), event_log_path=str(events))
        assert bad["snapshot"]["status"] == "rejected"
        assert recovered.export_state()["request_history"] == before["request_history"]
        print("[PASS] invalid snapshot is rejected without destroying live state")

        fresh = LMStudioGateway(max_retries=0, snapshot_path=str(Path(td) / "missing.json"), event_log_path=str(Path(td) / "missing.jsonl"))
        empty = fresh.restore_runtime()
        assert not empty["restored_any"]
        assert empty["snapshot"]["status"] == "missing"
        assert empty["event_log"]["status"] == "missing"
        print("[PASS] missing persistence files are handled safely")

        auto = LMStudioGateway(max_retries=0, snapshot_path=str(snap), event_log_path=str(events), auto_restore=True)
        # Snapshot is intentionally invalid, so automatic recovery must not raise.
        assert auto.diagnostics()["last_recovery"]["snapshot"]["status"] == "rejected"
        print("[PASS] optional startup auto-restore fails safe")

        # Ensure recovery reports remain JSON-safe and contain no prompt payloads.
        text = json.dumps(auto.diagnostics(), ensure_ascii=False)
        assert "secret" not in text
        print("[PASS] recovery diagnostics remain JSON-safe and secret-safe")

    print("\nSetup 4.29 tests complete.")


if __name__ == "__main__":
    main()
