import re
from pathlib import Path

from parsers.linux_security_parser import read_text_file


def parse_linux_server_info(
    server_folder: str | Path
) -> dict:
    """
    Parse hostname, IP address, OS, and execution time
    from サーバー情報.txt.
    """

    folder = Path(server_folder)

    file_path = folder / "サーバー情報.txt"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Linux server information file not found: "
            f"{file_path}"
        )

    content = read_text_file(
        file_path
    )

    hostname_match = re.search(
        r"\bip-\d+(?:-\d+){3}\b",
        content,
        re.IGNORECASE
    )

    ip_matches = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        content
    )

    os_match = re.search(
        r"(Ubuntu[^\r\n]*)",
        content,
        re.IGNORECASE
    )

    execution_time_match = re.search(
        r"\b20\d{2}-\d{2}-\d{2}\s+"
        r"\d{2}:\d{2}:\d{2}\s*(?:UTC)?",
        content
    )

    return {
        "hostname": (
            hostname_match.group(0)
            if hostname_match
            else folder.name
        ),
        "ip_addresses": list(
            dict.fromkeys(ip_matches)
        ),
        "execution_time": (
            execution_time_match.group(0)
            if execution_time_match
            else ""
        ),
        "operating_system": (
            os_match.group(1).strip()
            if os_match
            else "Linux"
        ),
    }