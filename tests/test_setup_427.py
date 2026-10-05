"""AZIZ AI SETUP 4.27 TEST - persistent runtime snapshots."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
import json
import requests
from core.models.lm_studio import LMStudioGateway

def response(content="ok"):
    r=Mock(); r.status_code=200; r.raise_for_status.return_value=None
    r.json.return_value={"choices":[{"message":{"content":content}}]}
    return r

def main():
    print("="*60); print("AZIZ AI SETUP 4.27 TEST"); print("="*60)
    with TemporaryDirectory() as td:
        path=Path(td)/"runtime.json"
        g=LMStudioGateway(max_retries=0, request_history_limit=3, snapshot_path=str(path))
        with patch("core.models.lm_studio.requests.post", return_value=response("ok")):
            assert g.chat([{"role":"user","content":"private prompt"}])=="ok"
        saved=g.save_snapshot()
        assert Path(saved).exists()
        raw=Path(saved).read_text(encoding="utf-8")
        assert "private prompt" not in raw and "choices" not in raw and "payload" not in raw
        data=json.loads(raw); assert data["snapshot_version"]==1
        print("[PASS] runtime snapshot is persisted as safe JSON without payloads")
        restored=LMStudioGateway(max_retries=0, request_history_limit=3, snapshot_path=str(path))
        assert restored.load_snapshot() is True
        assert restored.health==g.health
        assert restored.telemetry==g.telemetry
        assert restored.request_history==g.request_history
        assert restored.stats==g.stats
        print("[PASS] saved snapshot restores health, telemetry, history, and stats")
        before=path.read_text(encoding="utf-8")
        g.save_snapshot(); assert path.read_text(encoding="utf-8")==before
        print("[PASS] repeated saves replace the snapshot atomically")
        path.write_text(json.dumps({"snapshot_version":999}), encoding="utf-8")
        try: restored.load_snapshot()
        except ValueError: pass
        else: raise AssertionError("invalid snapshot version accepted")
        print("[PASS] corrupted/unsupported snapshots are rejected safely")
    print("\nSetup 4.27 tests complete.")
if __name__=="__main__": main()
