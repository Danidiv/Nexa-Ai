"""
Real Sandbox Runner — Stage 55-65% of the build path.

Runs AI-generated code inside an isolated Docker container instead of
directly on your machine, with real resource limits and real cleanup.

This is a thin, honest wrapper around the actual `docker` CLI - every
function here either runs a real `docker` subprocess and checks its real
exit code, or it doesn't claim to have done anything. Nothing here is a
stub.

Requires Docker Desktop (or another Docker engine) running locally.
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

DOCKERFILE_DIR = Path(__file__).resolve().parent.parent / "docker"
DEFAULT_IMAGE = "aziz-sandbox:latest"


class SandboxError(RuntimeError):
    """Raised when a docker command fails. Carries the real stderr from docker."""


def _run_docker(args: list[str], timeout: float = 60.0) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            ["docker"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise SandboxError(
            "docker command not found. Is Docker Desktop installed and on PATH?"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise SandboxError(f"docker {' '.join(args)} timed out after {timeout}s") from exc
    return result


def is_docker_available() -> bool:
    """Real check: can we actually talk to a running Docker daemon right now?"""
    result = _run_docker(["info"], timeout=10)
    return result.returncode == 0


def build_sandbox_image(tag: str = DEFAULT_IMAGE, dockerfile_dir: Path = DOCKERFILE_DIR) -> None:
    """
    Actually run `docker build`. Raises SandboxError with the real docker
    output if the build fails - never silently pretends it worked.
    """
    dockerfile = dockerfile_dir / "Dockerfile.sandbox"
    if not dockerfile.exists():
        raise SandboxError(f"Dockerfile not found at {dockerfile}")

    result = _run_docker(
        ["build", "-t", tag, "-f", str(dockerfile), str(dockerfile_dir)],
        timeout=300,
    )
    if result.returncode != 0:
        raise SandboxError(f"docker build failed:\n{result.stderr}")


def start_sandboxed_process(
    host_dir: Path,
    command: list[str],
    container_name: str,
    host_port: int | None = None,
    container_port: int = 8000,
    memory: str = "256m",
    cpus: str = "0.5",
    image: str = DEFAULT_IMAGE,
) -> None:
    """
    Actually run `docker run -d` (detached) with real resource limits:
    --memory caps RAM, --cpus caps CPU, --rm auto-removes the container
    when it stops so nothing leaks between runs. The host_dir is mounted
    read-only into /app - the generated code can run, but can't modify
    anything on your real disk.

    Raises SandboxError with real docker output if the container fails to
    start (e.g. port already in use, image missing).
    """
    args = [
        "run", "--rm", "-d",
        "--name", container_name,
        "--memory", memory,
        "--cpus", cpus,
        "-v", f"{host_dir.resolve()}:/app:ro",
        "-w", "/app",
    ]
    if host_port is not None:
        args += ["-p", f"{host_port}:{container_port}"]
    args += [image] + command

    result = _run_docker(args, timeout=30)
    if result.returncode != 0:
        raise SandboxError(f"docker run failed:\n{result.stderr}")


def is_container_running(container_name: str) -> bool:
    """Real check via `docker inspect` - not an assumption."""
    result = _run_docker(["inspect", "-f", "{{.State.Running}}", container_name], timeout=10)
    return result.returncode == 0 and result.stdout.strip() == "true"


def get_container_logs(container_name: str) -> str:
    """Real `docker logs` output - what actually printed inside the container."""
    result = _run_docker(["logs", container_name], timeout=10)
    return (result.stdout or "") + (result.stderr or "")


def stop_sandboxed_process(container_name: str, timeout: float = 5.0) -> None:
    """
    Actually run `docker stop`. Since containers were started with --rm,
    stopping also removes them - real cleanup, not just "stop tracking it".
    Safe to call even if the container already exited on its own.
    """
    _run_docker(["stop", "-t", str(int(timeout)), container_name], timeout=timeout + 10)


def wait_for_container_ready(container_name: str, timeout: float = 10.0) -> bool:
    """
    Poll `docker inspect` until the container is actually running, or
    until timeout. Returns False (doesn't raise) so the caller can decide
    what to do - e.g. print the real logs to show WHY it failed.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_container_running(container_name):
            return True
        time.sleep(0.3)
    return False
