#!/usr/bin/env python3
"""
Real multi-file demo: one prompt -> several correctly-linked real files ->
running live preview.

    prompt -> generate_plan()          (model call #1)
           -> generate_file_content()  (model call per file)
           -> write_multifile_project()  (real files on disk)
           -> verify_references()        (catches broken links)
           -> LivePreview.start()        (real running server)

Usage:
    python3 run_multifile_demo.py "a login page with separate CSS and JS"

Requires LM Studio running locally (default http://localhost:1234/v1).
"""
import sys
import time
import socket
import contextlib

from load_env import load_env
load_env()

from core.models.lm_studio import LMStudioGateway
from services.real_multifile_builder import build_multifile_project
from services.completion_live_preview import LivePreview


def _free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 run_multifile_demo.py "a login page with separate CSS and JS"')
        sys.exit(1)

    description = " ".join(sys.argv[1:])
    task_id = "multi-" + str(int(time.time()))

    print(f"[1/4] Planning files for: {description!r}")
    gateway = LMStudioGateway()

    try:
        project_dir, plan, problems = build_multifile_project(gateway, task_id, description)
    except ValueError as exc:
        print(f"      Generation failed: {exc}")
        sys.exit(1)

    print(f"[2/4] Plan: {[p.path for p in plan]}")
    print(f"      Written to: {project_dir}")

    if problems:
        print("[3/4] WARNING - reference problems found:")
        for p in problems:
            print(f"      - {p}")
    else:
        print("[3/4] All file references check out.")

    # find the html entry point, if any, for a nicer message
    html_files = [p.path for p in plan if p.path.endswith(".html")]
    entry = html_files[0] if html_files else plan[0].path

    print("[4/4] Starting live preview server...")
    port = _free_port()
    preview = LivePreview(
        command=["python3", "-m", "http.server", str(port), "--directory", str(project_dir)],
        url=f"http://localhost:{port}/{entry}",
    )
    if not preview.start():
        print("      Failed to start preview server.")
        sys.exit(1)

    time.sleep(0.5)
    print(f"      Open: {preview.state.url}")
    print(f"      Healthy: {preview.healthy()}")
    print("      Press Ctrl+C to stop.")

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
