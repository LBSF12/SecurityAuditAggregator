from pathlib import Path


WINDOWS_INDICATOR_FILES = {
    "3-1_auditpolicy.txt",
    "4-1_passwordpolicy.inf",
    "7_privilegedauditpolicy.txt",
    "securitypolicy.inf",
}

LINUX_INDICATOR_FILES = {
    "etc_passwd.txt",
    "etc_shadow.txt",
    "auditd.conf",
    "sshd_config",
    "linux_server_info.txt",
}


def read_server_info(server_folder: str | Path) -> str:
    """
    Read ServerInfo.txt content when available.
    """

    folder = Path(server_folder)

    possible_names = [
        "ServerInfo.txt",
        "server_info.txt",
        "serverinfo.txt",
        "サーバー情報.txt",
    ]

    for file_name in possible_names:
        file_path = folder / file_name

        if not file_path.exists():
            continue

        try:
            return file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            ).lower()

        except OSError:
            return ""

    return ""


def detect_operating_system(
    server_folder: str | Path
) -> str:
    """
    Detect whether a server evidence folder belongs
    to Windows or Linux.

    Returns:
        "windows"
        "linux"

    Raises:
        ValueError when detection is not reliable.
    """

    folder = Path(server_folder)

    if not folder.exists():
        raise FileNotFoundError(
            f"Server folder not found: {folder}"
        )

    if not folder.is_dir():
        raise ValueError(
            f"Server path is not a folder: {folder}"
        )

    server_info = read_server_info(folder)

    # First detection method:
    # use operating-system information written in ServerInfo.txt.
    windows_keywords = [
        "windows",
        "microsoft windows",
        "windows server",
    ]

    linux_keywords = [
        "linux",
        "ubuntu",
        "red hat",
        "rhel",
        "centos",
        "rocky linux",
        "alma linux",
        "debian",
        "suse",
    ]

    if any(
        keyword in server_info
        for keyword in windows_keywords
    ):
        return "windows"

    if any(
        keyword in server_info
        for keyword in linux_keywords
    ):
        return "linux"

    # Second detection method:
    # inspect evidence filenames.
    file_names = {
        file.name.lower()
        for file in folder.rglob("*")
        if file.is_file()
    }

    windows_score = len(
        file_names.intersection(
            WINDOWS_INDICATOR_FILES
        )
    )

    linux_score = len(
        file_names.intersection(
            LINUX_INDICATOR_FILES
        )
    )

    if windows_score > linux_score and windows_score > 0:
        return "windows"

    if linux_score > windows_score and linux_score > 0:
        return "linux"

    raise ValueError(
        "Unable to detect operating system for "
        f"server folder: {folder}"
    )