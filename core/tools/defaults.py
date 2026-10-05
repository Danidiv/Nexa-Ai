from .registry import ToolRegistry

from .commands import run_command
from .vscode import open_vscode

from .project import (
    create_project,
    list_projects,
)

from .project_commands import (
    run_project_command,
)

from .project_files import (
    write_project_file,
    read_project_file,
    edit_project_file,
    list_project_files,
)

from .files import (
    read_file,
    write_file,
    edit_file,
    list_files,
    create_folder,
)

from .python import run_python


def create_default_registry() -> ToolRegistry:
    """
    Create the standard Aziz AI tool registry.
    """

    registry = ToolRegistry()

    registry.register(
        "read_file",
        read_file,
    )

    registry.register(
        "write_file",
        write_file,
    )

    registry.register(
        "edit_file",
        edit_file,
    )

    registry.register(
        "list_files",
        list_files,
    )

    registry.register(
        "create_folder",
        create_folder,
    )

    registry.register(
        "run_python",
        run_python,
    )

    registry.register(
        "run_command",
        run_command,
    )

    registry.register(
        "open_vscode",
        open_vscode,
    )

    registry.register(
        "create_project",
        create_project,
    )

    registry.register(
        "list_projects",
        list_projects,
    )

    registry.register(
        "write_project_file",
        write_project_file,
    )

    registry.register(
        "read_project_file",
        read_project_file,
    )

    registry.register(
        "list_project_files",
        list_project_files,
    )

    registry.register(
        "run_project_command",
        run_project_command,
    )

    registry.register(
        "edit_project_file",
        edit_project_file,
    )

    return registry