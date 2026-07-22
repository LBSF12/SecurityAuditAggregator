from pathlib import Path


def read_file(file_path):
    """
    Read a text file using multiple possible encodings.

    Accepts:
        str or pathlib.Path

    Returns:
        tuple:
            (content, encoding_used)
    """

    # Convert a string path into a Path object.
    file_path = Path(file_path)

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp932",      # Japanese Windows
        "shift_jis",
        "utf-16",
        "latin1"
    ]

    for encoding in encodings:
        try:
            content = file_path.read_text(encoding=encoding)
            return content, encoding

        except UnicodeDecodeError:
            continue

    raise Exception(f"Unable to decode file: {file_path}")


def read_all_files(folder):
    """
    Read every TXT and INF file inside one extracted server folder.

    Returns:
        dict
    """

    folder = Path(folder)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    files = {}

    supported_extensions = [".txt", ".inf"]

    for file in folder.iterdir():

        if not file.is_file():
            continue

        if file.suffix.lower() not in supported_extensions:
            continue

        content, encoding = read_file(file)

        files[file.name] = {
            "content": content,
            "encoding": encoding
        }

    return files


def find_requirement_files(server_folder, requirement_prefix):
    """
    Find all files belonging to one requirement.

    Examples:
        requirement_prefix = "7"
        requirement_prefix = "9-1"

    Works for both Windows and Linux filenames.
    """

    server_folder = Path(server_folder)

    if not server_folder.exists():
        raise FileNotFoundError(
            f"Folder not found: {server_folder}"
        )

    matching_files = []

    prefix = f"{requirement_prefix}_"

    for file in server_folder.iterdir():

        if not file.is_file():
            continue

        if file.name.startswith(prefix):
            matching_files.append(file)

    return sorted(matching_files)