import os
import re


PROJECTS_DIR = os.path.abspath("projects")


def safe_project_name(name):
    """
    Convert a project name into a safe Windows folder name.
    """

    name = name.strip()

    # Remove unsafe characters
    name = re.sub(r'[<>:"/\\|?*]', "", name)

    # Replace spaces with underscores
    name = name.replace(" ", "_")

    # Prevent empty names
    if not name:
        return None

    return name


def create_project(name: str):
    """
    Create a new project inside the projects directory.
    """

    safe_name = safe_project_name(name)

    if not safe_name:
        return "ERROR: Invalid project name."

    os.makedirs(PROJECTS_DIR, exist_ok=True)

    project_path = os.path.join(PROJECTS_DIR, safe_name)

    if os.path.exists(project_path):
        return f"ERROR: Project already exists: {safe_name}"

    os.makedirs(project_path)

    return (
        f"SUCCESS: Project created successfully.\n"
        f"Name: {safe_name}\n"
        f"Path: {project_path}"
    )


def list_projects():
    """
    List all projects.
    """

    os.makedirs(PROJECTS_DIR, exist_ok=True)

    items = []

    for name in sorted(os.listdir(PROJECTS_DIR)):

        path = os.path.join(PROJECTS_DIR, name)

        if os.path.isdir(path):
            items.append(f"[PROJECT] {name}")

    if not items:
        return "No projects found."

    return "\n".join(items)