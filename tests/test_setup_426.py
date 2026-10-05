"""AZIZ AI SETUP 4.26 TEST - runtime snapshot export/restore."""
from unittest.mock import Mock, patch
import requests
from core.models.lm_studio import LMStudioGateway

def response(status=200, content="ok"):
    r=Mock(); r.status_code=status
    if status >= 400: r.raise_for_status.side_effect=requests.HTTPError(f"HTTP {status}", response=r)
    else: r.raise_for_status.return_value=None
    r.json.return_value={"choices":[{"message":{"content":content}}]}
    return r

def main():
    print("="*60); print("AZIZ AI SETUP 4.26 TEST"); print("="*60)
    g=LMStudioGateway(max_retries=0, retry_delay=0, request_history_limit=3)
    with patch("core.models.lm_studio.requests.post", return_value=response(200,"ok")): g.chat([{"role":"user","content":"secret"}])
    snap=g.export_state(); text=__import__('json').dumps(snap)
    assert "secret" not in text and "messages" not in text and "payload" not in text
    print("[PASS] runtime snapshot is JSON-safe and excludes request payloads")
    h=LMStudioGateway(max_retries=0, request_history_limit=3); h.restore_state(snap)
    assert h.health==g.health and h.request_history==g.request_history and h.stats==g.stats
    assert h.telemetry["count"]==g.telemetry["count"]
    print("[PASS] health, telemetry, history, and stats restore correctly")
    h.reset_stats(); assert h.health["total_requests"]==0 and h.request_history==[] and h.stats["total_requests"]==0
    assert g.health["total_requests"]==1
    print("[PASS] reset remains independent after restore")
    try: h.restore_state({"snapshot_version":999})
    except ValueError: pass
    else: raise AssertionError("invalid version accepted")
    print("[PASS] invalid snapshot versions are rejected safely")
    print("\nSetup 4.26 tests complete.")
if __name__=="__main__": main()
