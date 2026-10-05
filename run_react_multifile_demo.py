#!/usr/bin/env python3
"""
Real multi-component React demo: one prompt -> several real, cross-linked
components -> real Vite dev server -> you open it in your browser.

    prompt -> generate_plan()                (model call #1: JSON file list)
           -> generate_component() per file   (model call per component)
           -> real Vite dev server
           -> EVERY component individually validated against the real
              compiler - not just App.jsx

Usage:
    python3 run_react_multifile_demo.py "a pricing page with three tier cards"
"""
import sys
import time

from load_env import load_env
load_env()

from core.models.lm_studio import LMStudioGateway
from services.real_react_multifile_builder import build_multi_component_react_app


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 run_react_multifile_demo.py "a pricing page with three tier cards"')
        sys.exit(1)

    description = " ".join(sys.argv[1:])
    task_id = "reactmulti-" + str(int(time.time()))

    print(f"[1/4] Planning components for: {description!r}")
    gateway = LMStudioGateway()

    try:
        project_dir, port, process, plan, problems = build_multi_component_react_app(
            gateway, task_id, description
        )
    except ValueError as exc:
        print(f"      Planning/generation failed: {exc}")
        sys.exit(1)

    print(f"[2/4] Plan: {[p.path for p in plan]}")
    print(f"      Scaffolded at: {project_dir}")

    if problems:
        print("[3/4] Vite could not compile one or more components:")
        for p in problems:
            print(f"      {p}")
        process.terminate()
        sys.exit(1)
    print("[3/4] All components compiled successfully.")

    print(f"[4/4] Dev server is live at: http://localhost:{port}/")
    print("      Open that in your browser now.")
    print("      Press Ctrl+C to stop.")

    try:
        while process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except Exception:
            process.kill()
        print("Dev server stopped.")


if __name__ == "__main__":
    main()
