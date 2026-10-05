from pathlib import Path


WORKSPACE = Path("workspace").resolve()


def _safe_path(path: str) -> Path:
    """
    Convert a workspace-relative path into a safe absolute path.
    Prevents access outside the Agent workspace.
    """

    file_path = (WORKSPACE / path).resolve()

    if WORKSPACE not in file_path.parents and file_path != WORKSPACE:
        raise ValueError(
            "Access outside the workspace is not allowed."
        )

    return file_path


def read_file(path: str) -> str:
    """
    Read a UTF-8 text file from the workspace.
    """

    try:

        file_path = _safe_path(path)

        if not file_path.exists():
            return f"ERROR: File not found: {path}"

        if not file_path.is_file():
            return f"ERROR: Not a file: {path}"

        try:

            return file_path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            return (
                f"ERROR: File is not a UTF-8 "
                f"text file: {path}"
            )

    except Exception as e:

        return f"ERROR reading file: {e}"


def write_file(path: str, content: str) -> str:
    """
    Create or overwrite a UTF-8 text file inside
    the Agent workspace.
    """

    try:

        file_path = _safe_path(path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        return (
            f"SUCCESS: File written successfully: {path}\n"
            f"Bytes written: {file_path.stat().st_size}"
        )

    except Exception as e:

        return f"ERROR writing file: {e}"


def edit_file(
    path: str,
    old_text: str,
    new_text: str
) -> str:
    """
    Safely replace exactly one occurrence of old_text
    inside an existing workspace file.

    This is intended for small, precise edits.
    """

    try:

        file_path = _safe_path(path)

        # --------------------------------------------
        # EXISTENCE
        # --------------------------------------------

        if not file_path.exists():

            return (
                f"ERROR: File not found: {path}"
            )

        if not file_path.is_file():

            return (
                f"ERROR: Not a file: {path}"
            )

        # --------------------------------------------
        # INPUT VALIDATION
        # --------------------------------------------

        if not isinstance(old_text, str):

            return (
                "ERROR: old_text must be a string."
            )

        if not isinstance(new_text, str):

            return (
                "ERROR: new_text must be a string."
            )

        if not old_text:

            return (
                "ERROR: old_text cannot be empty."
            )

        # --------------------------------------------
        # READ EXISTING FILE
        # --------------------------------------------

        try:

            content = file_path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            return (
                f"ERROR: File is not a UTF-8 "
                f"text file: {path}"
            )

        # --------------------------------------------
        # EXACT MATCH
        # --------------------------------------------

        count = content.count(old_text)

        if count == 0:

            return (
                "ERROR: The exact old_text was not "
                "found in the file.\n"
                "No changes were made."
            )

        if count > 1:

            return (
                f"ERROR: old_text occurs {count} times.\n"
                "The edit is ambiguous.\n"
                "No changes were made."
            )

        # --------------------------------------------
        # APPLY EXACTLY ONE EDIT
        # --------------------------------------------

        new_content = content.replace(
            old_text,
            new_text,
            1
        )

        # --------------------------------------------
        # WRITE
        # --------------------------------------------

        file_path.write_text(
            new_content,
            encoding="utf-8"
        )

        return (
            f"SUCCESS: File edited successfully: {path}\n"
            f"Replaced exactly one occurrence.\n"
            f"Bytes written: "
            f"{file_path.stat().st_size}"
        )

    except Exception as e:

        return f"ERROR editing file: {e}"


def list_files(path: str = ".") -> str:
    """
    List files and folders inside the Agent workspace.
    """

    try:

        folder = _safe_path(path)

        if not folder.exists():

            return (
                f"ERROR: Folder not found: {path}"
            )

        if not folder.is_dir():

            return (
                f"ERROR: Not a folder: {path}"
            )

        items = []

        for item in sorted(
            folder.iterdir(),
            key=lambda x: x.name.lower()
        ):

            if item.is_dir():

                items.append(
                    f"[DIR]  {item.name}"
                )

            else:

                items.append(
                    f"[FILE] {item.name}"
                )

        if not items:

            return (
                f"Folder is empty: {path}"
            )

        return "\n".join(items)

    except Exception as e:

        return (
            f"ERROR listing files: {e}"
        )


def create_folder(path: str) -> str:
    """
    Create a folder inside the Agent workspace.
    """

    try:

        folder = _safe_path(path)

        if folder.exists():

            if folder.is_dir():

                return (
                    f"INFO: Folder already exists: {path}"
                )

            return (
                f"ERROR: A file already exists at: {path}"
            )

        folder.mkdir(
            parents=True,
            exist_ok=False
        )

        return (
            f"SUCCESS: Folder created successfully: {path}"
        )

    except Exception as e:

        return (
            f"ERROR creating folder: {e}"
        )