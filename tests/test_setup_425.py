"""AZIZ AI SETUP 4.25 TEST - bounded request history."""
from unittest.mock import Mock, patch
import requests
from core.models.lm_studio import LMStudioGateway

def response(status=200, content="ok"):
    r = Mock(); r.status_code = status
    if status >= 400: r.raise_for_status.side_effect = requests.HTTPError(f"HTTP {status}", response=r)
    else: r.raise_for_status.return_value = None
    r.json.return_value = {"choices": [{"message": {"content": content}}]}
    return r

def main():
    print("=" * 60); print("AZIZ AI SETUP 4.25 TEST"); print("=" * 60)
    g = LMStudioGateway(max_retries=1, retry_delay=0, retry_jitter=0, request_history_limit=3)
    with patch("core.models.lm_studio.requests.post", side_effect=[response(503), response(200, "ok")]):
        assert g.chat([{"role":"user","content":"test"}]) == "ok"
    h=g.request_history; assert len(h)==1 and h[0]["outcome"]=="success" and h[0]["attempts"]==2
    assert isinstance(h[0]["request_id"], str) and h[0]["request_id"] and "messages" not in h[0]
    print("[PASS] logical requests are recorded with safe identifiers")
    g=LMStudioGateway(max_retries=0, retry_delay=0, request_history_limit=3)
    with patch("core.models.lm_studio.requests.post", side_effect=[response(503)]):
        try: g.chat([{"role":"user","content":"fail"}])
        except requests.HTTPError: pass
    assert len(g.request_history)==1 and g.request_history[0]["outcome"]=="failure"
    assert g.request_history[0]["error_category"]=="transient_http" and g.request_history[0]["status_code"]==503
    print("[PASS] failed logical requests preserve safe failure details")
    for i in range(4): g._request_history.record({"request_id":str(i),"outcome":"success","attempts":1,"duration_seconds":0.0})
    assert len(g.request_history)==3 and [x["request_id"] for x in g.request_history]==["1","2","3"]
    print("[PASS] request history remains bounded")
    d=g.diagnostics(); assert "request_history" in d and d["request_history"]==g.request_history
    g.reset_stats(); assert g.request_history==[]
    print("[PASS] diagnostics and reset expose and clear request history")
    print("\nSetup 4.25 tests complete.")
if __name__ == "__main__": main()
