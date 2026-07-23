import re
import unicodedata
from pathlib import Path
from typing import Optional

from parsers.linux_security_parser import read_text_file


SERVER_INFO_FILE_ALIASES = {
    "サーバー情報.txt",
    "serverinfo.txt",
    "server_info.txt",
    "server-information.txt",
    "server_information.txt",
    "linux_server_info.txt",
    "linux-server-info.txt",
}


def normalize_filename(filename: str) -> str:
    """
    Normalize a filename so that harmless differences between
    Windows ZIP extraction and Linux ZIP extraction do not
    prevent matching.

    The normalization:
        - converts Unicode to NFKC form;
        - removes leading and trailing spaces;
        - compares without capitalization differences.
    """

    return unicodedata.normalize(
        "NFKC",
        filename
    ).strip().casefold()


def looks_like_server_information(
    content: str
) -> bool:
    """
    Determine whether text content appears to be the Linux
    server-information evidence file.

    This fallback is useful when a Japanese filename becomes
    corrupted or differently encoded during ZIP extraction.
    """

    if not content:
        return False

    score = 0

    # Operating-system evidence.
    if re.search(
        r"\b(?:ubuntu|linux|debian|centos|rhel|red\s+hat|"
        r"rocky|alma|suse|amazon\s+linux)\b",
        content,
        re.IGNORECASE
    ):
        score += 1

    # IPv4 address.
    if re.search(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        content
    ):
        score += 1

    # Linux-style hostname such as ip-172-31-41-116.
    if re.search(
        r"\bip-\d+(?:-\d+){3}\b",
        content,
        re.IGNORECASE
    ):
        score += 1

    # Collection timestamp.
    if re.search(
        r"\b20\d{2}-\d{2}-\d{2}\s+"
        r"\d{2}:\d{2}:\d{2}",
        content
    ):
        score += 1

    # Kernel version or kernel label.
    if re.search(
        r"\bkernel\b|"
        r"\b\d+\.\d+\.\d+-\d+",
        content,
        re.IGNORECASE
    ):
        score += 1

    # Require at least two independent indicators.
    return score >= 2


def find_linux_server_info_file(
    server_folder: str | Path
) -> Path:
    """
    Find the Linux server-information file safely.

    Search order:
        1. Known filename aliases.
        2. Normalized recursive filename comparison.
        3. Content-based detection across TXT files.

    Raises:
        FileNotFoundError when no suitable evidence file exists.
    """

    folder = Path(server_folder)

    if not folder.exists():
        raise FileNotFoundError(
            f"Linux server folder not found: {folder}"
        )

    if not folder.is_dir():
        raise NotADirectoryError(
            f"Linux server path is not a directory: {folder}"
        )

    normalized_aliases = {
        normalize_filename(alias)
        for alias in SERVER_INFO_FILE_ALIASES
    }

    candidate_files = [
        path
        for path in folder.rglob("*")
        if path.is_file()
    ]

    # First try known names using normalized comparison.
    for candidate in candidate_files:
        normalized_candidate = normalize_filename(
            candidate.name
        )

        if normalized_candidate in normalized_aliases:
            return candidate

    # Fall back to inspecting text-file contents.
    text_extensions = {
        ".txt",
        ".log",
        ".conf",
        ""
    }

    for candidate in candidate_files:
        if candidate.suffix.casefold() not in text_extensions:
            continue

        try:
            content = read_text_file(candidate)
        except Exception:
            continue

        if looks_like_server_information(content):
            return candidate

    discovered_files = "\n".join(
        f"  - {path.relative_to(folder)}"
        for path in candidate_files
    )

    raise FileNotFoundError(
        "Linux server information file could not be identified.\n"
        f"Search folder: {folder}\n"
        "Accepted names include:\n"
        + "\n".join(
            f"  - {name}"
            for name in sorted(SERVER_INFO_FILE_ALIASES)
        )
        + "\nDiscovered files:\n"
        + (
            discovered_files
            if discovered_files
            else "  No files discovered."
        )
    )


def extract_hostname(
    content: str,
    fallback: str
) -> str:
    """
    Extract the hostname from server-information content.
    """

    # Standard English-style label.
    labeled_match = re.search(
        r"(?im)^\s*(?:hostname|host\s*name)\s*[:=]\s*(.+?)\s*$",
        content
    )

    if labeled_match:
        return labeled_match.group(1).strip()

    # Common AWS/Linux hostname.
    aws_hostname_match = re.search(
        r"\bip-\d+(?:-\d+){3}\b",
        content,
        re.IGNORECASE
    )

    if aws_hostname_match:
        return aws_hostname_match.group(0)

    # General Linux hostname pattern after a colon or separator.
    general_match = re.search(
        r"(?im)^\s*[^:\r\n]{0,30}[:：]\s*"
        r"([a-zA-Z0-9][a-zA-Z0-9._-]{1,253})\s*$",
        content
    )

    if general_match:
        candidate = general_match.group(1).strip()

        # Avoid returning operating-system names or timestamps.
        if not re.search(
            r"ubuntu|linux|utc|kernel",
            candidate,
            re.IGNORECASE
        ):
            return candidate

    return fallback


def extract_ip_addresses(
    content: str
) -> list[str]:
    """
    Extract valid IPv4 addresses while preserving order.
    """

    matches = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        content
    )

    valid_addresses = []

    for address in matches:
        octets = address.split(".")

        if all(
            0 <= int(octet) <= 255
            for octet in octets
        ):
            if address not in valid_addresses:
                valid_addresses.append(address)

    return valid_addresses


def extract_operating_system(
    content: str
) -> str:
    """
    Extract the Linux distribution and version.
    """

    distribution_patterns = [
        r"(Ubuntu[^\r\n]*)",
        r"(Debian[^\r\n]*)",
        r"(CentOS[^\r\n]*)",
        r"(Red Hat[^\r\n]*)",
        r"(RHEL[^\r\n]*)",
        r"(Rocky Linux[^\r\n]*)",
        r"(AlmaLinux[^\r\n]*)",
        r"(SUSE[^\r\n]*)",
        r"(Amazon Linux[^\r\n]*)",
    ]

    for pattern in distribution_patterns:
        match = re.search(
            pattern,
            content,
            re.IGNORECASE
        )

        if match:
            operating_system = match.group(1).strip()

            # Remove common separators left before the value.
            operating_system = operating_system.lstrip(
                ":：=-・"
            ).strip()

            return operating_system

    if re.search(
        r"\blinux\b",
        content,
        re.IGNORECASE
    ):
        return "Linux"

    return "Linux"


def extract_execution_time(
    content: str
) -> str:
    """
    Extract the evidence collection timestamp.
    """

    match = re.search(
        r"\b20\d{2}-\d{2}-\d{2}\s+"
        r"\d{2}:\d{2}:\d{2}"
        r"(?:\s+[A-Z]{2,5})?",
        content
    )

    if match:
        return match.group(0).strip()

    return ""


def parse_linux_server_info(
    server_folder: str | Path
) -> dict:
    """
    Parse hostname, IP addresses, OS and execution time
    from the Linux server-information evidence.

    The file is located dynamically rather than requiring the
    exact filename サーバー情報.txt.
    """

    folder = Path(server_folder)

    server_info_file = find_linux_server_info_file(
        folder
    )

    content = read_text_file(
        server_info_file
    )

    hostname = extract_hostname(
        content,
        fallback=folder.name
    )

    ip_addresses = extract_ip_addresses(
        content
    )

    operating_system = extract_operating_system(
        content
    )

    execution_time = extract_execution_time(
        content
    )

    return {
        "hostname": hostname,
        "ip_addresses": ip_addresses,
        "execution_time": execution_time,
        "operating_system": operating_system,
        "server_info_file": str(
            server_info_file
        ),
    }