#!/usr/bin/env python3
"""
Real end-to-end demo: prompt -> generated file -> running live preview.

This is the ONE real chain from the roadmap's Phase 3, wired together
using pieces that already existed in the project:

    core/models/lm_studio.py      (model gateway -- already built)
    services/real_frontend_builder.py   (NEW -- actually generates code)
    services/completion_live_preview.py (already built -- actually runs a process)

Usage:
    python3 run_frontend_demo.py "a login page with a dashboard"

Requires LM Studio running locally (default http://localhost:1234/v1).
"""
import sys
import time
import socket
import contextlib

from load_env import load_env
load_env()

from core.models.lm_studio import LMStudioGateway
from services.real_frontend_builder import build_frontend
from services.completion_live_preview import LivePreview


def _free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 run_frontend_demo.py "a login page with a dashboard"')
        sys.exit(1)

    description = " ".join(sys.argv[1:])
    task_id = "demo-" + str(int(time.time()))

    print(f"[1/3] Generating frontend for: {description!r}")
    gateway = LMStudioGateway()
    index_path, dangling, dom_problems = build_frontend(gateway, task_id, description)
    print(f"      Written to: {index_path}")
    if dangling:
        print(f"      Note: model referenced {dangling} which don't exist - auto-removed, inline content kept.")
    if dom_problems:
        print("      WARNING: the JS references elements that don't exist in the HTML:")
        for problem in dom_problems:
            print(f"        - {problem}")
        print("      This page may look fine but silently fail/error when used. Not auto-fixed.")

    print("[2/3] Starting live preview server...")
    port = _free_port()
    preview = LivePreview(
        command=["python3", "-m", "http.server", str(port), "--directory", str(index_path.parent)],
        url=f"http://localhost:{port}",
    )
    started = preview.start()
    if not started:
        print("      Failed to start preview server.")
        sys.exit(1)

    time.sleep(0.5)  # give the server a moment to bind

    print("[3/3] Done.")
    print(f"      Open: {preview.state.url}")
    print(f"      Healthy: {preview.healthy()}")
    print("      Press Ctrl+C to stop the preview server.")

    try:
        while preview.healthy():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        preview.stop()
        print("Preview stopped.")


if __name__ == "__main__":
    main()
