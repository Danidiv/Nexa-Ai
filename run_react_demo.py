#!/usr/bin/env python3
"""
Real React demo: prompt -> real component -> real Vite dev server -> you
open it in your browser.

    prompt -> generate_app_component()  (real model call)
           -> scaffold_react_project()  (real files + symlinked node_modules)
           -> start_vite_dev_server()   (real npm run dev)
           -> validate_via_dev_server() (real compile check)

Usage:
    python3 run_react_demo.py "a pricing page with three tiers"

Requires:
    - LM Studio running locally
    - react_scaffold_test/node_modules already installed (run
      `npm install` inside react_scaffold_test/ once, if you haven't)
"""
import sys
import time

from load_env import load_env
load_env()

from core.models.lm_studio import LMStudioGateway
from services.real_react_builder import build_react_app


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 run_react_demo.py "a pricing page with three tiers"')
        sys.exit(1)

    description = " ".join(sys.argv[1:])
    task_id = "react-" + str(int(time.time()))

    print(f"[1/3] Generating React component for: {description!r}")
    gateway = LMStudioGateway()

    project_dir, port, process, problems = build_react_app(gateway, task_id, description)
    print(f"      Scaffolded at: {project_dir}")

    if problems:
        print("[2/3] Vite could not compile the generated component:")
        for p in problems:
            print(f"      {p}")
        process.terminate()
        sys.exit(1)

    print("[2/3] Vite compiled the component successfully.")
    print(f"[3/3] Dev server is live at: http://localhost:{port}/")
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
