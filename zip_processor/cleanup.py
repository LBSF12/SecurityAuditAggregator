import shutil
from pathlib import Path


def cleanup_directory(
    directory: str | Path
) -> None:
    """
    Delete a temporary directory safely.
    """

    directory_path = Path(directory)

    if not directory_path.exists():
        return

    if not directory_path.is_dir():
        raise ValueError(
            f"Cleanup target is not a directory: "
            f"{directory_path}"
        )

    shutil.rmtree(
        directory_path
    )