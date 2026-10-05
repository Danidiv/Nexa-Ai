import os


PROJECTS_DIR = os.path.abspath("projects")


def get_project_path(project):
    """Return the absolute path of a project safely."""

    project = project.strip()

    if not project:
        return None

    # Prevent path traversal
    if (
        ".." in project
        or "/" in project
        or "\\" in project
        or ":" in project
    ):
        return None

    project_path = os.path.abspath(
        os.path.join(PROJECTS_DIR, project)
    )

    # Make sure it stays inside projects/
    if not project_path.startswith(PROJECTS_DIR + os.sep):
        return None

    if not os.path.isdir(project_path):
        return None

    return project_path


def safe_file_path(project_path, file_path):
    """Create a safe path inside a project."""

    file_path = file_path.strip()

    if not file_path:
        return None

    full_path = os.path.abspath(
        os.path.join(project_path, file_path)
    )

    # Prevent escaping the project directory
    if not full_path.startswith(project_path + os.sep):
        return None

    return full_path


def write_project_file(project:str, path:str, content:str):
    """Create or overwrite a file inside a project."""

    project_path = get_project_path(project)

    if not project_path:
        return "ERROR: Invalid or unknown project."

    full_path = safe_file_path(project_path, path)

    if not full_path:
        return "ERROR: Invalid file path."

    try:
        # Create parent directories if necessary
        parent = os.path.dirname(full_path)

        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(
            full_path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(content)

        return (
            "SUCCESS: Project file written successfully.\n"
            f"Project: {project}\n"
            f"File: {path}\n"
            f"Path: {full_path}\n"
            f"Bytes written: {len(content.encode('utf-8'))}"
        )

    except Exception as e:
        return f"ERROR writing project file: {e}"

def read_project_file(project: str, path: str):
    """Read a file inside an existing project."""

    project_path = get_project_path(project)

    if not project_path:
        return "ERROR: Invalid or unknown project."

    full_path = safe_file_path(project_path, path)

    if not full_path:
        return "ERROR: Invalid file path."

    if not os.path.isfile(full_path):
        return f"ERROR: File not found: {path}"

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        return (
            "SUCCESS: Project file read successfully.\n"
            f"Project: {project}\n"
            f"File: {path}\n"
            f"Content:\n{content}"
        )

    except Exception as e:
        return f"ERROR reading project file: {e}"
def list_project_files(project: str):
    """List files and folders inside a project."""

    project_path = get_project_path(project)

    if not project_path:
        return "ERROR: Invalid or unknown project."

    try:
        results = []

        for root, dirs, files in os.walk(project_path):

            # Sort for consistent output
            dirs.sort()
            files.sort()

            relative_root = os.path.relpath(
                root,
                project_path
            )

            if relative_root == ".":
                relative_root = ""

            for directory in dirs:
                if relative_root:
                    path = os.path.join(
                        relative_root,
                        directory
                    )
                else:
                    path = directory

                results.append(f"[DIR]  {path}")

            for file in files:
                if relative_root:
                    path = os.path.join(
                        relative_root,
                        file
                    )
                else:
                    path = file

                results.append(f"[FILE] {path}")

        if not results:
            return "Project is empty."

        return "\n".join(results)

    except Exception as e:
        return f"ERROR listing project files: {e}"

def edit_project_file(project: str, path: str, old_text: str, new_text: str):
    """
    Make a small, exact text replacement inside a project file.

    The file must already exist.
    old_text must occur exactly once.
    """

    project_path = get_project_path(project)

    if not project_path:
        return "ERROR: Invalid or unknown project."

    full_path = safe_file_path(project_path, path)

    if not full_path:
        return "ERROR: Invalid file path."

    if not os.path.isfile(full_path):
        return f"ERROR: File not found: {path}"

    if not isinstance(old_text, str) or not isinstance(new_text, str):
        return "ERROR: old_text and new_text must be strings."

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        count = content.count(old_text)

        if count == 0:
            return (
                "ERROR: old_text was not found in the project file.\n"
                f"Project: {project}\n"
                f"File: {path}"
            )

        if count > 1:
            return (
                "ERROR: old_text occurs multiple times in the project file. "
                "Refusing to make an ambiguous edit.\n"
                f"Occurrences: {count}"
            )

        new_content = content.replace(
            old_text,
            new_text,
            1
        )

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return (
            "SUCCESS: Project file edited successfully.\n"
            f"Project: {project}\n"
            f"File: {path}\n"
            "Replacement count: 1\n"
            f"Bytes written: {len(new_content.encode('utf-8'))}"
        )

    except UnicodeDecodeError:
        return f"ERROR: Project file is not UTF-8 text: {path}"

    except Exception as e:
        return f"ERROR editing project file: {e}"