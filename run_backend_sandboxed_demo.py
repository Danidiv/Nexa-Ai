#!/usr/bin/env python3
"""
Real SANDBOXED backend demo - same as run_backend_demo.py, but the
generated server actually runs inside an isolated Docker container
instead of directly on your machine.

    prompt -> generate + validate backend (same as before)
           -> docker build (once, cached after first run)
           -> docker run -d --memory=256m --cpus=0.5 --rm  (REAL isolation)
           -> real HTTP request to the mapped port
           -> docker stop  (REAL cleanup)

Usage:
    python3 run_backend_sandboxed_demo.py "a login endpoint, admin/1234"

Requires Docker Desktop running.
"""
import sys
import time
import urllib.request
import urllib.error

from load_env import load_env
load_env()

from core.models.lm_studio import LMStudioGateway
from services.real_backend_builder import build_backend
from services.sandbox_runner import (
    SandboxError,
    is_docker_available,
    build_sandbox_image,
    start_sandboxed_process,
    stop_sandboxed_process,
    wait_for_container_ready,
    is_container_running,
    get_container_logs,
)


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 run_backend_sandboxed_demo.py "a login endpoint, admin/1234"')
        sys.exit(1)

    description = " ".join(sys.argv[1:])
    task_id = "sandboxed-" + str(int(time.time()))
    container_name = f"aziz-{task_id}"

    print("[1/6] Checking Docker is available...")
    try:
        if not is_docker_available():
            print("      Docker daemon not responding. Is Docker Desktop running?")
            sys.exit(1)
    except SandboxError as exc:
        print(f"      {exc}")
        sys.exit(1)
    print("      Docker is available.")

    print("[2/6] Building sandbox image (cached after first run)...")
    try:
        build_sandbox_image()
    except SandboxError as exc:
        print(f"      Image build failed:\n{exc}")
        sys.exit(1)
    print("      Image ready.")

    print(f"[3/6] Generating backend for: {description!r}")
    gateway = LMStudioGateway()
    server_path, problems, auto_fixed = build_backend(gateway, task_id, description)
    print(f"      Written to: {server_path}")
    if auto_fixed:
        print("      Auto-fixed before validation:")
        for fix in auto_fixed:
            print(f"        - {fix}")
    if problems:
        print("      Syntax/structure problems found - NOT running this file:")
        for p in problems:
            print(f"        - {p}")
        sys.exit(1)
    print("      Syntax check passed.")

    print("[4/6] Starting backend INSIDE an isolated container...")
    try:
        start_sandboxed_process(
            host_dir=server_path.parent,
            command=["python3", "server.py"],
            container_name=container_name,
            host_port=8000,
            container_port=8000,
        )
    except SandboxError as exc:
        print(f"      Failed to start container:\n{exc}")
        sys.exit(1)

    ready = wait_for_container_ready(container_name, timeout=10)
    if not ready:
        print("      Container did not stay running. Logs:")
        print("      " + get_container_logs(container_name).replace("\n", "\n      "))
        sys.exit(1)
    print(f"      Container '{container_name}' is running (memory-limited, CPU-limited, read-only mount).")

    print("[5/6] Sending a real test request to http://localhost:8000/ ...")
    print("      (trying GET first, then POST - these backends are typically POST-only)")
    got_response = False
    try:
        resp = urllib.request.urlopen("http://localhost:8000/", timeout=5)
        print(f"      GET Status: {resp.status}  Body: {resp.read().decode(errors='replace')[:300]}")
        got_response = True
    except urllib.error.HTTPError as exc:
        print(f"      GET Status: {exc.code} (server responded - method just not supported, that's fine)")
        got_response = True
    except Exception:
        print("      GET: connection closed without a clean response (some servers do this for "
              "unsupported methods) - trying a POST instead, since that's what a login endpoint needs:")
        try:
            req = urllib.request.Request(
                "http://localhost:8000/",
                data=b'{"username": "test", "password": "test"}',
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=5)
            print(f"      POST Status: {resp.status}  Body: {resp.read().decode(errors='replace')[:300]}")
            got_response = True
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            print(f"      POST Status: {exc.code}  Body: {body[:300]}")
            got_response = True
        except Exception as exc2:
            print(f"      POST also failed: {exc2}")

    if not got_response:
        print("      Server may not be fully ready yet - check with your own curl command below.")

    print()
    print(f"[6/6] Sandbox is live at http://localhost:8000/ (container: {container_name})")
    print("      Try your own curl/POST requests now if you want.")
    print("      Press Ctrl+C to stop and clean up the container.")

    try:
        while is_container_running(container_name):
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping and removing container...")
        stop_sandboxed_process(container_name)
        print("Done - container fully removed (--rm).")


if __name__ == "__main__":
    main()
