#!/usr/bin/env python3
"""
Real backend demo: one prompt -> real Python backend file -> actually run
it as a subprocess -> actually send it a real HTTP request -> show the
real response.

    prompt -> generate_backend_code()   (model call)
           -> validate_python_syntax()  (real ast.parse check)
           -> write to disk             (real file)
           -> subprocess.Popen()        (real running server)
           -> urllib request            (real HTTP call, real response)

Usage:
    python3 run_backend_demo.py "a login endpoint that checks username and password"
"""
import sys
import time
import subprocess
import urllib.request
import urllib.error

from load_env import load_env
load_env()

from core.models.lm_studio import LMStudioGateway
from services.real_backend_builder import build_backend


def _wait_for_server(url: str, timeout: float = 10.0) -> bool:
    """Poll the URL until it responds or timeout - real, observable readiness check."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except urllib.error.HTTPError:
            return True  # server IS up, just returned a non-2xx status - still "ready"
        except Exception:
            time.sleep(0.3)
    return False


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 run_backend_demo.py "a login endpoint that checks username and password"')
        sys.exit(1)

    description = " ".join(sys.argv[1:])
    task_id = "backend-" + str(int(time.time()))

    print(f"[1/4] Generating backend for: {description!r}")
    gateway = LMStudioGateway()

    server_path, problems, auto_fixed = build_backend(gateway, task_id, description)
    print(f"      Written to: {server_path}")
    if auto_fixed:
        print("      Auto-fixed before validation:")
        for fix in auto_fixed:
            print(f"        - {fix}")

    if problems:
        print("[2/4] Syntax/structure problems found - NOT running this file:")
        for p in problems:
            print(f"        - {p}")
        sys.exit(1)
    print("[2/4] Syntax check passed - safe to run.")

    print("[3/4] Starting backend as a real subprocess...")
    proc = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    base_url = "http://localhost:8000/"
    ready = _wait_for_server(base_url, timeout=10)

    if not ready:
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=5)
        print("      Server did not respond within 10 seconds.")
        if stderr:
            print("      --- stderr from the process ---")
            print(stderr[-1500:])
        sys.exit(1)

    print("      Server is up and responding.")
    print("[4/4] Sending a real GET request to http://localhost:8000/ ...")
    try:
        resp = urllib.request.urlopen(base_url, timeout=5)
        body = resp.read().decode("utf-8", errors="replace")
        print(f"      Status: {resp.status}")
        print(f"      Body:   {body[:500]}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"      Status: {exc.code} (server responded, just not with 2xx)")
        print(f"      Body:   {body[:500]}")
    except Exception as exc:
        print(f"      Request failed: {exc}")

    print()
    print("      Server is still running at http://localhost:8000/")
    print("      Try your own requests (e.g. curl -X POST ... ) now if you want.")
    print("      Press Ctrl+C to stop it.")

    try:
        while proc.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Backend stopped.")


if __name__ == "__main__":
    main()
