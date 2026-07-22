from pathlib import Path
from uuid import uuid4

from zip_processor.zip_extractor import extract_zip


SERVER_INFO_NAMES = {
    "serverinfo.txt",
    "server_info.txt",
    "サーバー情報.txt",
}


def is_server_folder(folder: str | Path) -> bool:
    """
    Determine whether a folder appears to contain
    one server's audit evidence.
    """

    folder_path = Path(folder)

    if not folder_path.is_dir():
        return False

    file_names = {
        file.name.lower()
        for file in folder_path.iterdir()
        if file.is_file()
    }

    return bool(
        SERVER_INFO_NAMES.intersection(file_names)
    )


def find_server_folders(
    root_folder: str | Path
) -> list[Path]:
    """
    Recursively find folders containing ServerInfo.txt
    or server_info.txt.
    """

    root_path = Path(root_folder)

    if not root_path.exists():
        return []

    server_folders = []

    if is_server_folder(root_path):
        server_folders.append(root_path)

    for folder in root_path.rglob("*"):

        if folder.is_dir() and is_server_folder(folder):
            server_folders.append(folder)

    unique_folders = []

    seen = set()

    for folder in server_folders:

        resolved_folder = folder.resolve()

        if resolved_folder not in seen:
            seen.add(resolved_folder)
            unique_folders.append(folder)

    return unique_folders


def find_nested_zip_files(
    root_folder: str | Path
) -> list[Path]:
    """
    Find ZIP files inside an extracted customer package.
    """

    root_path = Path(root_folder)

    return sorted(
        file
        for file in root_path.rglob("*.zip")
        if file.is_file()
    )


def process_input_zip(
    input_zip: str | Path,
    temp_root: str | Path = "temp"
) -> list[Path]:
    """
    Process one ZIP input.

    Supports:

    1. A ZIP containing one server's audit evidence.
    2. A customer ZIP containing multiple server ZIPs.
    3. A ZIP containing already extracted server folders.

    Returns
    -------
    list[Path]:
        Extracted server folders ready for evaluation.
    """

    input_zip_path = Path(input_zip)

    if not input_zip_path.exists():
        raise FileNotFoundError(
            f"Input ZIP not found: {input_zip_path}"
        )

    temp_root_path = Path(temp_root)

    session_folder = (
        temp_root_path
        / f"audit_{uuid4().hex}"
    )

    root_extraction_folder = (
        session_folder
        / "root"
    )

    extract_zip(
        input_zip_path,
        root_extraction_folder
    )

    server_folders = find_server_folders(
        root_extraction_folder
    )

    nested_zip_files = find_nested_zip_files(
        root_extraction_folder
    )

    nested_extraction_root = (
        session_folder
        / "servers"
    )

    for index, nested_zip in enumerate(
        nested_zip_files,
        start=1
    ):
        safe_zip_name = nested_zip.stem.replace(
            " ",
            "_"
        )

        extraction_folder = (
            nested_extraction_root
            / f"{index:03d}_{safe_zip_name}"
        )

        try:
            extract_zip(
                nested_zip,
                extraction_folder
            )

        except Exception as error:
            print(
                f"Warning: Could not extract "
                f"{nested_zip.name}: {error}"
            )
            continue

        extracted_servers = find_server_folders(
            extraction_folder
        )

        server_folders.extend(
            extracted_servers
        )

    unique_server_folders = []

    seen = set()

    for folder in server_folders:

        resolved_folder = folder.resolve()

        if resolved_folder not in seen:
            seen.add(resolved_folder)
            unique_server_folders.append(folder)

    return unique_server_folders