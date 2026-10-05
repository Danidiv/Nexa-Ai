import shlex
import subprocess


# Commands that Aziz is currently allowed to run.
ALLOWED_COMMANDS = {
    "python",
    "python3",
    "pip",
    "dir",
    "type",
    "where",
    "echo",
    "mkdir",
    "code",
}

# Operators that must never appear in an approved command.
# We never pass shell=True, so these can't chain commands even if present,
# but we still reject them explicitly so failures are clear rather than silent.
DANGEROUS_TOKENS = {"&&", "||", "|", ";", ">", ">>", "<", "`", "$("}


def run_command(command: str):
    """
    Run a controlled command safely (no shell interpretation).

    Only commands in ALLOWED_COMMANDS are permitted, and the command is
    executed as a literal argv list -- never through a shell -- so operators
    like &&, ;, |, or backticks cannot chain additional commands.
    """

    command = command.strip()

    if not command:
        return "ERROR: Empty command."

    try:
        # posix=False keeps Windows-style paths (backslashes) intact.
        parts = shlex.split(command, posix=False)
    except ValueError as e:
        return f"ERROR: Could not parse command: {e}"

    if not parts:
        return "ERROR: Empty command."

    for token in parts:
        if token in DANGEROUS_TOKENS:
            return (
                f"ERROR: Command contains a disallowed operator: '{token}'. "
                "Only a single command may be run at a time."
            )

    executable = parts[0].lower()
    executable = executable.removesuffix(".exe")
    executable = executable.removesuffix(".cmd")

    if executable not in ALLOWED_COMMANDS:
        return (
            f"ERROR: Command '{parts[0]}' is not allowed.\n"
            f"Allowed commands: {', '.join(sorted(ALLOWED_COMMANDS))}"
        )

    try:
        result = subprocess.run(
            parts,
            shell=False,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="workspace"
        )

        output = []
        output.append(f"Exit code: {result.returncode}")

        if result.stdout:
            output.append("\nSTDOUT:")
            output.append(result.stdout)

        if result.stderr:
            output.append("\nSTDERR:")
            output.append(result.stderr)

        return "\n".join(output)

    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out after 30 seconds."

    except FileNotFoundError:
        return f"ERROR: Executable not found: {parts[0]}"

    except Exception as e:
        return f"ERROR: Could not execute command: {e}"
