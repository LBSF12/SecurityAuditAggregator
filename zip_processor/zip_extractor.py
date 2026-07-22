from pathlib import Path
from zipfile import BadZipFile, ZipFile


class UnsafeZipError(Exception):
    """
    Raised when a ZIP contains an unsafe file path.
    """


def _is_safe_member(
    destination: Path,
    member_name: str
) -> bool:
    """
    Prevent ZIP path traversal such as:

        ../../malicious_file.txt
    """

    destination = destination.resolve()

    target_path = (
        destination / member_name
    ).resolve()

    try:
        target_path.relative_to(destination)
        return True

    except ValueError:
        return False


def extract_zip(
    zip_path: str | Path,
    destination: str | Path
) -> Path:
    """
    Safely extract a ZIP file.

    Parameters
    ----------
    zip_path:
        ZIP file to extract.

    destination:
        Extraction destination.

    Returns
    -------
    Path:
        Extracted folder path.
    """

    zip_file = Path(zip_path)
    destination_folder = Path(destination)

    if not zip_file.exists():
        raise FileNotFoundError(
            f"ZIP file not found: {zip_file}"
        )

    if zip_file.suffix.lower() != ".zip":
        raise ValueError(
            f"Input file is not a ZIP: {zip_file}"
        )

    destination_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    try:
        with ZipFile(zip_file, "r") as archive:

            for member in archive.infolist():

                if not _is_safe_member(
                    destination_folder,
                    member.filename
                ):
                    raise UnsafeZipError(
                        "Unsafe path found in ZIP: "
                        f"{member.filename}"
                    )

            archive.extractall(
                destination_folder
            )

    except BadZipFile as error:
        raise BadZipFile(
            f"Invalid or corrupted ZIP file: {zip_file}"
        ) from error

    return destination_folder