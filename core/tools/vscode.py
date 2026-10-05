import subprocess
import os


def open_vscode(path: str | None = None):
    """
    Open a folder or file in Visual Studio Code.
    """

    path = path.strip()

    if not path:
        path = "."

    # Convert relative path to absolute path
    if not os.path.isabs(path):
        path = os.path.abspath(os.path.join("workspace", path))

    if not os.path.exists(path):
        return f"ERROR: Path does not exist: {path}"

    try:
        subprocess.Popen(
            ["code", path],
            shell=True
        )

        return f"SUCCESS: VS Code opened: {path}"

    except Exception as e:
        return f"ERROR: Could not open VS Code: {e}"