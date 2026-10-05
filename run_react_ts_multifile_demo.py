#!/usr/bin/env python3
"""
Real React + TypeScript + shadcn/ui demo: one prompt -> real typed
components using real shadcn primitives -> real Vite dev server -> real
tsc type-check.

Usage:
    python3 run_react_ts_multifile_demo.py "a pricing page with three tier cards"
"""
import sys
import time

from load_env import load_env
load_env()

from core.models.lm_studio import LMStudioGateway
from services.real_react_ts_multifile_builder import build_multi_component_react_ts_app


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 run_react_ts_multifile_demo.py "a pricing page with three tier cards"')
        sys.exit(1)

    description = " ".join(sys.argv[1:])
    task_id = "reactts-" + str(int(time.time()))

    print(f"[1/5] Planning TypeScript components for: {description!r}")
    gateway = LMStudioGateway()

    try:
        project_dir, port, process, plan, problems = build_multi_component_react_ts_app(
            gateway, task_id, description
        )
    except ValueError as exc:
        print(f"      Planning/generation failed: {exc}")
        sys.exit(1)

    print(f"[2/5] Plan: {[p.path for p in plan]}")
    print(f"      Scaffolded at: {project_dir}")

    if problems:
        print("[3/5] Problems found:")
        for p in problems:
            print(f"      {p}")
        process.terminate()
        sys.exit(1)
    print("[3/5] All components compiled, prop-checked, AND type-checked cleanly.")
    print("[4/5] Real shadcn/ui primitives (Button, Card, Input) were available to the model.")

    print(f"[5/5] Dev server is live at: http://localhost:{port}/")
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
