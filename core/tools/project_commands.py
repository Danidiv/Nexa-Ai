import shlex
import subprocess

from .project_files import get_project_path


ALLOWED_COMMANDS = {
    "python",
    "python3",
    "pip",
}

DANGEROUS_TOKENS = {"&&", "||", "|", ";", ">", ">>", "<", "`", "$("}


def run_project_command(project: str, command: str):
    """
    Run an allowed command inside a project directory, safely.

    Executed as a literal argv list (no shell), so operators like &&, ;, |
    can't be used to chain in extra commands.
    """

    project_path = get_project_path(project)

    if not project_path:
        return "ERROR: Invalid or unknown project."

    command = command.strip()

    if not command:
        return "ERROR: Command cannot be empty."

    try:
        parts = shlex.split(command, posix=False)
    except ValueError as e:
        return f"ERROR: Could not parse command: {e}"

    if not parts:
        return "ERROR: Command cannot be empty."

    for token in parts:
        if token in DANGEROUS_TOKENS:
            return (
                f"ERROR: Command contains a disallowed operator: '{token}'. "
                "Only a single command may be run at a time."
            )

    executable = parts[0].lower()

    if executable not in ALLOWED_COMMANDS:
        return (
            f"ERROR: Command '{executable}' is not allowed.\n"
            f"Allowed commands: {', '.join(sorted(ALLOWED_COMMANDS))}"
        )

    try:
        result = subprocess.run(
            parts,
            cwd=project_path,
            shell=False,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = []
        output.append(f"Exit code: {result.returncode}")

        if result.stdout:
            output.append(f"\nSTDOUT:\n{result.stdout}")

        if result.stderr:
            output.append(f"\nSTDERR:\n{result.stderr}")

        return "\n".join(output)

    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out after 30 seconds."

    except FileNotFoundError:
        return f"ERROR: Executable not found: {parts[0]}"

    except Exception as e:
        return f"ERROR running project command: {e}"
