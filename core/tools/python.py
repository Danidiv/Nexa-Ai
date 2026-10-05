from pathlib import Path
import subprocess
import sys


WORKSPACE = Path("workspace").resolve()


def _safe_python_path(path: str) -> Path:
    """
    Resolve a Python file inside the Agent workspace.
    """

    file_path = (WORKSPACE / path).resolve()

    if WORKSPACE not in file_path.parents:
        raise ValueError(
            "Python file must be inside the Agent workspace."
        )

    if file_path.suffix.lower() != ".py":
        raise ValueError(
            "Only .py files can be executed."
        )

    return file_path


def run_python(path: str, timeout: int = 10) -> str:
    """
    Execute a Python file inside the Agent workspace.
    """

    try:

        file_path = _safe_python_path(path)

        if not file_path.exists():
            return f"ERROR: Python file not found: {path}"

        if not file_path.is_file():
            return f"ERROR: Not a file: {path}"

        result = subprocess.run(
            [
                sys.executable,
                str(file_path)
            ],
            cwd=str(file_path.parent),
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = []

        output.append(
            f"Exit code: {result.returncode}"
        )

        if result.stdout:
            output.append(
                "\nSTDOUT:\n" + result.stdout
            )

        if result.stderr:
            output.append(
                "\nSTDERR:\n" + result.stderr
            )

        if result.returncode == 0:
            output.insert(
                0,
                "SUCCESS: Python program completed."
            )
        else:
            output.insert(
                0,
                "ERROR: Python program failed."
            )

        return "\n".join(output)

    except subprocess.TimeoutExpired:

        return (
            "ERROR: Python program exceeded "
            f"the {timeout}-second timeout."
        )

    except Exception as e:

        return f"ERROR running Python: {e}"