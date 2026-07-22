from pathlib import Path
from typing import Any

from analyzers.linux_server_engine import evaluate_linux_server
from analyzers.os_detector import detect_operating_system
from analyzers.server_engine import evaluate_windows_server


def evaluate_server(
    server_folder: str | Path
) -> Any:
    """
    Detect the operating system of a server audit folder
    and run the corresponding evaluation engine.

    Supported operating systems:
        - Windows
        - Linux
    """

    server_folder = Path(
        server_folder
    )

    if not server_folder.exists():
        raise FileNotFoundError(
            "Server audit folder does not exist: "
            f"{server_folder}"
        )

    if not server_folder.is_dir():
        raise NotADirectoryError(
            "The supplied server path is not a directory: "
            f"{server_folder}"
        )

    operating_system = detect_operating_system(
        server_folder
    )

    if not operating_system:
        raise ValueError(
            "Operating-system detection returned "
            f"no result for: {server_folder}"
        )

    normalized_os = str(
        operating_system
    ).strip().lower()

    print(
        "Detected operating system: "
        f"{normalized_os.upper()}"
    )

    if normalized_os == "windows":
        return evaluate_windows_server(
            server_folder
        )

    if normalized_os == "linux":
        return evaluate_linux_server(
            server_folder
        )

    raise ValueError(
        "Unsupported operating system detected: "
        f"{operating_system}. "
        f"Folder: {server_folder}"
    )