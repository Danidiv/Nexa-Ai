"""
Real Multi-User Web UI Server — Stage 85-95% of the build path.

Adds to the single-user version:
  - real accounts + sessions (services/user_store.py)
  - per-user isolated workspaces (workspace/user_<id>/...)
  - a real sequential job queue (one worker thread) so concurrent users
    don't send simultaneous requests to the one local model at once
  - per-user backend ports, so two users' generated backends don't fight
    over port 8000

Run with:
    python3 -m uvicorn web_ui.server:app --port 8080
"""
from __future__ import annotations

import queue
import socket
import subprocess
import sys
import threading
import time
import uuid
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from load_env import load_env
load_env()

from core.models.lm_studio import LMStudioGateway
from services.real_multifile_builder import build_multifile_project
from services.real_backend_builder import build_backend
from services.real_react_multifile_builder import build_multi_component_react_app
# NOTE: real_react_ts_builder.py also defines a function with this exact
# same name (an older, single-shot version with no retry on a missing
# default export). Importing both under the same name here used to let
# the second import silently shadow the first, so the React+TS build
# path was actually running the older builder the whole time while
# real_react_ts_multifile_builder.py sat unused. Only the intended
# multi-file builder is imported now.
from services.real_react_ts_multifile_builder import build_multi_component_react_ts_app
from services.real_codebase_index import index_project
from services import user_store

WORKSPACE_DIR = Path(__file__).resolve().parent.parent / "workspace"
WORKSPACE_DIR.mkdir(exist_ok=True)

user_store.init_db()

_react_template_dir = Path(__file__).resolve().parent.parent / "react_scaffold_test"
if not (_react_template_dir / "node_modules").exists():
    _sep = "=" * 70
    print(
        "\n" + _sep + "\n"
        "WARNING: React mode will fail until you run this once:\n"
        f"    cd {_react_template_dir.name}\n"
        "    npm install\n"
        "Website and Backend modes work fine without this.\n"
        + _sep + "\n"
    )

app = FastAPI(title="AZIZ AI Web UI")

_tasks: dict[str, dict] = {}
_tasks_lock = threading.Lock()

_build_queue: "queue.Queue[tuple[str, int, str, str]]" = queue.Queue()  # (task_id, user_id, mode, prompt)

# Per-user backend process tracking - each user gets their OWN port, so
# two users' generated backends never collide.
_user_backends: dict[int, dict] = {}  # user_id -> {"process": Popen, "port": int}
_user_backends_lock = threading.Lock()

# Each user's live Vite dev server - separate tracking from the plain
# backend one above, since a user could have both running at once.
_user_react_servers: dict[int, dict] = {}  # user_id -> {"process": Popen, "port": int}
_user_react_servers_lock = threading.Lock()

SESSION_COOKIE = "aziz_session"


def _log(task_id: str, message: str) -> None:
    with _tasks_lock:
        if task_id in _tasks:
            _tasks[task_id]["logs"].append(message)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _get_current_user_id(request: Request) -> int:
    token = request.cookies.get(SESSION_COOKIE)
    user_id = user_store.get_user_id_for_session(token) if token else None
    if user_id is None:
        raise HTTPException(401, "not logged in")
    return user_id


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class AuthRequest(BaseModel):
    username: str
    password: str


@app.post("/api/signup")
def signup(req: AuthRequest, response: Response):
    try:
        user_id = user_store.create_user(req.username, req.password)
    except user_store.UserError as exc:
        raise HTTPException(400, str(exc))
    token = user_store.create_session(user_id)
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax")
    return {"username": req.username}


@app.post("/api/login")
def login(req: AuthRequest, response: Response):
    try:
        user_id = user_store.verify_login(req.username, req.password)
    except user_store.UserError as exc:
        raise HTTPException(401, str(exc))
    token = user_store.create_session(user_id)
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax")
    return {"username": req.username}


@app.post("/api/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        user_store.delete_session(token)
    response.delete_cookie(SESSION_COOKIE)
    return {"ok": True}


@app.get("/api/me")
def me(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    user_id = user_store.get_user_id_for_session(token) if token else None
    if user_id is None:
        raise HTTPException(401, "not logged in")
    return {"username": user_store.get_username(user_id)}


# ---------------------------------------------------------------------------
# Build pipeline (real sequential worker thread - the real "job queue")
# ---------------------------------------------------------------------------

def _process_website_build(task_id: str, user_id: int, prompt: str) -> None:
    try:
        user_dir = user_store.user_workspace_dir(user_id, WORKSPACE_DIR)
        _log(task_id, f"Planning files for: {prompt!r}")
        gateway = LMStudioGateway()
        project_dir, plan, problems = build_multifile_project(gateway, task_id, prompt, workspace_dir=str(user_dir))
        _log(task_id, f"Plan: {[p.path for p in plan]}")
        if problems:
            _log(task_id, "Warnings:")
            for p in problems:
                _log(task_id, f"  - {p}")
        else:
            _log(task_id, "All file references check out.")

        html_files = [p.path for p in plan if p.path.endswith(".html")]
        entry = html_files[0] if html_files else plan[0].path
        _log(task_id, f"Done. Preview entry point: {entry}")

        with _tasks_lock:
            _tasks[task_id]["status"] = "done"
            _tasks[task_id]["project_dir"] = str(project_dir)
            _tasks[task_id]["entry"] = entry
    except Exception as exc:
        _log(task_id, f"Build failed: {exc}")
        with _tasks_lock:
            _tasks[task_id]["status"] = "error"
            _tasks[task_id]["error"] = str(exc)


def _process_backend_build(task_id: str, user_id: int, prompt: str) -> None:
    try:
        user_dir = user_store.user_workspace_dir(user_id, WORKSPACE_DIR)
        _log(task_id, f"Generating backend for: {prompt!r}")
        gateway = LMStudioGateway()
        server_path, problems, auto_fixed = build_backend(gateway, task_id, prompt, workspace_dir=str(user_dir))

        if auto_fixed:
            _log(task_id, "Auto-fixed before validation:")
            for fix in auto_fixed:
                _log(task_id, f"  - {fix}")

        if problems:
            _log(task_id, "Syntax/structure problems found - NOT running this file:")
            for p in problems:
                _log(task_id, f"  - {p}")
            with _tasks_lock:
                _tasks[task_id]["status"] = "error"
                _tasks[task_id]["error"] = "; ".join(problems)
            return

        _log(task_id, "Syntax check passed.")

        # Each user gets their OWN port - stopping only THEIR previous
        # backend, never another user's.
        with _user_backends_lock:
            existing = _user_backends.get(user_id)
            if existing and existing["process"].poll() is None:
                _log(task_id, "Stopping your previous backend...")
                existing["process"].terminate()
                try:
                    existing["process"].wait(timeout=5)
                except subprocess.TimeoutExpired:
                    existing["process"].kill()

            port = _free_port()
            _log(task_id, f"Starting your backend as a subprocess on port {port}...")
            process = subprocess.Popen(
                [sys.executable, str(server_path), str(port)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            _user_backends[user_id] = {"process": process, "port": port}

        ready = False
        for _ in range(20):
            if process.poll() is not None:
                break
            try:
                import urllib.request
                urllib.request.urlopen(f"http://localhost:{port}/", timeout=1)
                ready = True
                break
            except Exception:
                time.sleep(0.3)

        if process.poll() is not None:
            _, stderr = process.communicate()
            _log(task_id, f"Backend crashed on startup:\n{stderr[-800:]}")
            with _tasks_lock:
                _tasks[task_id]["status"] = "error"
                _tasks[task_id]["error"] = "Backend crashed on startup"
            return

        _log(task_id, f"Backend is running on your own port: {port}")
        with _tasks_lock:
            _tasks[task_id]["status"] = "done"
            _tasks[task_id]["port"] = port
    except Exception as exc:
        _log(task_id, f"Build failed: {exc}")
        with _tasks_lock:
            _tasks[task_id]["status"] = "error"
            _tasks[task_id]["error"] = str(exc)


def _process_react_build(task_id: str, user_id: int, prompt: str) -> None:
    try:
        user_dir = user_store.user_workspace_dir(user_id, WORKSPACE_DIR)
        _log(task_id, f"Planning React components for: {prompt!r}")
        gateway = LMStudioGateway()

        def runtime_probe():
            with _tasks_lock:
                task = _tasks.get(task_id, {})
                runtime = dict(task.get("runtime", {}))
                runtime["consumed_ready_seq"] = task.get("runtime_consumed_ready_seq", 0)
                return runtime

        def runtime_status(status, revision, message, **meta):
            with _tasks_lock:
                task = _tasks.get(task_id)
                if not task:
                    return
                task["status"] = status
                task["runtime_revision"] = revision
                if status == "verifying_runtime" and revision > 0:
                    task.setdefault("runtime", {"ready_seq": 0, "errors": [], "events": 0})["errors"] = []
                if meta.get("project_dir"):
                    task["project_dir"] = meta["project_dir"]
                if meta.get("port"):
                    task["port"] = meta["port"]
            _log(task_id, message)

        def progress(stage, message, **meta):
            # Structured live activity: the sidebar receives these exact
            # milestones while the builder is working. Error events include
            # the best-known file and compiler/runtime diagnostic.
            prefix = {
                "planning": "Planning", "coding": "Writing code",
                "imports": "Checking imports", "scaffold": "Preparing project",
                "build": "Running build", "typecheck": "Type-checking",
                "error": "Bug found", "repair": "Fixing code",
            }.get(stage, stage.title())
            _log(task_id, f"{prefix}: {message}")
            if meta.get("file"):
                _log(task_id, f"  File: {meta['file']}")
            err = meta.get("error")
            if err:
                text = str(err)
                if len(text) > 1400:
                    text = text[-1400:]
                _log(task_id, f"  Problem: {text}")

        project_dir, port, process, plan, problems = build_multi_component_react_app(
            gateway, task_id, prompt, workspace_dir=str(user_dir),
            runtime_probe=runtime_probe, runtime_status=runtime_status,
            progress=progress, max_repairs=5,
            runtime_token=_tasks.get(task_id, {}).get("runtime_token"),
        )
        _log(task_id, f"Plan: {[p.path for p in plan]}")

        if problems:
            _log(task_id, "Problems found after automatic repair attempts:")
            for p in problems:
                _log(task_id, f"  - {p}")
            _log(task_id, "Automatic repair stopped at the configured retry limit; the last diagnostic is shown above.")
            process.terminate()
            with _tasks_lock:
                _tasks[task_id]["status"] = "error"
                _tasks[task_id]["error"] = "; ".join(problems)
            return

        _log(task_id, "All components compiled and prop-checked cleanly.")

        # One live Vite server per user - stop any previous one first.
        with _user_react_servers_lock:
            existing = _user_react_servers.get(user_id)
            if existing and existing["process"].poll() is None:
                _log(task_id, "Stopping your previous React dev server...")
                existing["process"].terminate()
                try:
                    existing["process"].wait(timeout=5)
                except subprocess.TimeoutExpired:
                    existing["process"].kill()
            _user_react_servers[user_id] = {"process": process, "port": port}

        _log(task_id, f"React dev server is running on your own port: {port}")
        with _tasks_lock:
            _tasks[task_id]["status"] = "done"
            _tasks[task_id]["port"] = port
            _tasks[task_id]["files"] = [{"path": p.path, "type": "jsx"} for p in plan]
    except Exception as exc:
        _log(task_id, f"Build failed: {exc}")
        with _tasks_lock:
            _tasks[task_id]["status"] = "error"
            _tasks[task_id]["error"] = str(exc)


def _process_react_ts_build(task_id: str, user_id: int, prompt: str) -> None:
    try:
        user_dir = user_store.user_workspace_dir(user_id, WORKSPACE_DIR)
        _log(task_id, f"Planning React+TypeScript components for: {prompt!r}")
        gateway = LMStudioGateway()

        def runtime_probe():
            with _tasks_lock:
                task = _tasks.get(task_id, {})
                return dict(task.get("runtime", {}))

        def runtime_status(status, revision, message, **meta):
            with _tasks_lock:
                task = _tasks.get(task_id)
                if not task:
                    return
                task["status"] = status
                task["runtime_revision"] = revision
                if status == "verifying_runtime" and revision > 0:
                    task.setdefault("runtime", {"ready_seq": 0, "errors": [], "events": 0})["errors"] = []
                if meta.get("project_dir"):
                    task["project_dir"] = meta["project_dir"]
                if meta.get("port"):
                    task["port"] = meta["port"]
            _log(task_id, message)


        def progress(stage, message, **meta):
            prefix = {
                "planning": "Planning", "coding": "Writing code",
                "imports": "Checking imports", "scaffold": "Preparing project",
                "build": "Running build", "typecheck": "TypeScript validation",
                "error": "Bug found", "repair": "Fixing code",
            }.get(stage, stage.title())
            _log(task_id, f"{prefix}: {message}")
            if meta.get("file"):
                _log(task_id, f"  File: {meta['file']}")
            if meta.get("error"):
                text = str(meta["error"])
                if len(text) > 1400:
                    text = text[-1400:]
                _log(task_id, f"  Problem: {text}")

        project_dir, port, process, plan, problems = build_multi_component_react_ts_app(
            gateway, task_id, prompt, workspace_dir=str(user_dir), progress=progress,
            runtime_probe=runtime_probe, runtime_status=runtime_status, max_repairs=5,
            runtime_token=_tasks.get(task_id, {}).get("runtime_token"),
        )
        _log(task_id, f"Plan: {[p.path for p in plan]}")

        if problems:
            _log(task_id, "Problems found after automatic repair attempts:")
            for p in problems:
                _log(task_id, f"  - {p}")
            _log(task_id, "Automatic repair stopped at the configured retry limit; the last diagnostic is shown above.")
            process.terminate()
            with _tasks_lock:
                _tasks[task_id]["status"] = "error"
                _tasks[task_id]["error"] = "; ".join(problems)
            return

        _log(task_id, "All components compiled, prop-checked, and type-checked cleanly.")

        # Shares the same per-user "one active React server" slot as plain
        # React mode - starting either kind stops whichever was running.
        with _user_react_servers_lock:
            existing = _user_react_servers.get(user_id)
            if existing and existing["process"].poll() is None:
                _log(task_id, "Stopping your previous React dev server...")
                existing["process"].terminate()
                try:
                    existing["process"].wait(timeout=5)
                except subprocess.TimeoutExpired:
                    existing["process"].kill()
            _user_react_servers[user_id] = {"process": process, "port": port}

        _log(task_id, f"React+TS dev server is running on your own port: {port}")
        with _tasks_lock:
            _tasks[task_id]["status"] = "done"
            _tasks[task_id]["port"] = port
            _tasks[task_id]["files"] = [{"path": p.path, "type": "tsx"} for p in plan]
    except Exception as exc:
        _log(task_id, f"Build failed: {exc}")
        with _tasks_lock:
            _tasks[task_id]["status"] = "error"
            _tasks[task_id]["error"] = str(exc)


def _worker_loop() -> None:
    """
    The real job queue: ONE worker thread processes builds strictly one at
    a time, in the order they were submitted, regardless of how many users
    hit /api/build simultaneously. This matters because there is exactly
    ONE local model server (LM Studio) - letting many requests hit it at
    once would just make everyone's build slower and messier, not faster.
    """
    while True:
        task_id, user_id, mode, prompt = _build_queue.get()
        with _tasks_lock:
            _tasks[task_id]["status"] = "running"
        if mode == "website":
            _process_website_build(task_id, user_id, prompt)
        elif mode == "react":
            _process_react_build(task_id, user_id, prompt)
        elif mode == "react_ts":
            _process_react_ts_build(task_id, user_id, prompt)
        else:
            _process_backend_build(task_id, user_id, prompt)
        _build_queue.task_done()


_worker_thread = threading.Thread(target=_worker_loop, daemon=True)
_worker_thread.start()


class BuildRequest(BaseModel):
    prompt: str
    mode: str


@app.post("/api/build")
def start_build(req: BuildRequest, request: Request):
    user_id = _get_current_user_id(request)
    if req.mode not in ("website", "backend", "react", "react_ts"):
        raise HTTPException(400, "mode must be 'website', 'backend', 'react', or 'react_ts'")
    if not req.prompt.strip():
        raise HTTPException(400, "prompt is required")

    task_id = f"{req.mode}-{uuid.uuid4().hex[:8]}-{int(time.time())}"
    with _tasks_lock:
        _tasks[task_id] = {
            "status": "queued", "logs": [], "mode": req.mode,
            "project_dir": None, "error": None, "user_id": user_id,
            "runtime": {"ready_seq": 0, "errors": [], "events": 0}, "runtime_revision": 0,
            "runtime_token": secrets.token_urlsafe(24),
        }
    _build_queue.put((task_id, user_id, req.mode, req.prompt))
    return {"task_id": task_id}


@app.post("/api/runtime-errors/{task_id}")
async def runtime_error_report(task_id: str, request: Request):
    """Receive browser runtime/console evidence from a generated React iframe."""
    origin = request.headers.get("origin")
    with _tasks_lock:
        task = _tasks.get(task_id)
        if task is None:
            raise HTTPException(404, "unknown task_id")
        user_id = task.get("user_id")
    token = request.cookies.get(SESSION_COOKIE)
    session_user = user_store.get_user_id_for_session(token) if token else None
    runtime_token = request.headers.get("X-AZIZ-Runtime-Token") or request.query_params.get("runtime_token")
    if not runtime_token:
        try:
            raw_body_for_token = await request.body()
            import json as _json_for_token
            body_payload_for_token = _json_for_token.loads(raw_body_for_token.decode("utf-8", errors="replace"))
            if isinstance(body_payload_for_token, dict):
                runtime_token = body_payload_for_token.get("runtime_token")
        except Exception:
            pass
    task_runtime_token = task.get("runtime_token")
    if user_id is None or (session_user != user_id and runtime_token != task_runtime_token):
        raise HTTPException(403, "not your task")
    try:
        import json
        payload = json.loads((await request.body()).decode("utf-8", errors="replace"))
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    event_type = str(payload.get("type", "")).lower()
    with _tasks_lock:
        state = _tasks[task_id].setdefault("runtime", {"ready_seq": 0, "errors": [], "events": 0})
        state["events"] += 1
        if event_type == "error":
            event = {k: payload.get(k) for k in ("message", "stack", "filename", "line", "column", "component", "url")}
            signature = f"{event.get('message')}|{event.get('stack')}|{event.get('filename')}"
            if not any(e.get("_signature") == signature for e in state["errors"]):
                event["_signature"] = signature
                state["errors"].append(event)
            state["ready_seq"] = 0
        elif event_type == "ready":
            state["errors"] = []
            state["ready_seq"] += 1
            state["last_ready_at"] = time.time()
    response = JSONResponse({"ok": True})
    if origin and origin.startswith(("http://localhost:", "http://127.0.0.1:")):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.get("/api/status/{task_id}")
def get_status(task_id: str, request: Request):
    user_id = _get_current_user_id(request)
    with _tasks_lock:
        task = _tasks.get(task_id)
        if task is None:
            raise HTTPException(404, "unknown task_id")
        if task["user_id"] != user_id:
            raise HTTPException(403, "not your task")  # real per-user isolation
        result = dict(task)

    if result.get("project_dir"):
        try:
            index = index_project(Path(result["project_dir"]))
            result["files"] = [{"path": p, "type": s.file_type} for p, s in sorted(index.files.items())]
        except Exception:
            result["files"] = []
    return JSONResponse(result)


@app.get("/preview/{task_id}/{file_path:path}")
def preview_file(task_id: str, file_path: str, request: Request):
    user_id = _get_current_user_id(request)
    with _tasks_lock:
        task = _tasks.get(task_id)
    if task is None or task["user_id"] != user_id or not task.get("project_dir"):
        raise HTTPException(404, "no project for this task")

    full_path = (Path(task["project_dir"]) / file_path).resolve()
    project_root = Path(task["project_dir"]).resolve()
    if not str(full_path).startswith(str(project_root)):
        raise HTTPException(403, "invalid path")
    if not full_path.exists():
        raise HTTPException(404, "file not found")
    return FileResponse(full_path)


class TestBackendRequest(BaseModel):
    body: dict


@app.post("/api/test-backend")
def test_backend(req: TestBackendRequest, request: Request):
    import json
    import urllib.request
    import urllib.error

    user_id = _get_current_user_id(request)
    with _user_backends_lock:
        entry = _user_backends.get(user_id)
    if entry is None:
        raise HTTPException(400, "you don't have a backend running yet")

    try:
        r = urllib.request.Request(
            f"http://localhost:{entry['port']}/",
            data=json.dumps(req.body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(r, timeout=5)
        return {"status": resp.status, "body": resp.read().decode(errors="replace")}
    except urllib.error.HTTPError as exc:
        return {"status": exc.code, "body": exc.read().decode(errors="replace")}
    except Exception as exc:
        raise HTTPException(502, f"Your backend is not reachable: {exc}")


static_dir = Path(__file__).resolve().parent / "static"
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
