from typing import Any


def parse_log_retention(file_content: str) -> dict[str, Any]:
    """
    Parse Windows Security Event Log configuration.

    Example input:

        name: Security
        enabled: true
        type: Admin
        logging:
          logFileName: %SystemRoot%\\System32\\Winevt\\Logs\\Security.evtx
          retention: false
          autoBackup: false
          maxSize: 20971520
        publishing:
          fileMax: 1

    The parser collects the actual maximum size for reporting,
    but compliance validation should only check whether a valid
    size has been configured.
    """

    result: dict[str, Any] = {
        "LOG_ENABLED": None,
        "RETENTION": None,
        "AUTO_BACKUP": None,
        "MAX_SIZE_BYTES": None,
        "MAX_SIZE_MB": None,
        "MAX_SIZE_CONFIGURED": False,
    }

    for raw_line in file_content.splitlines():
        line = raw_line.strip()

        if not line or ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip()
        value = value.strip()

        if key == "enabled":
            result["LOG_ENABLED"] = parse_boolean(value)

        elif key == "retention":
            result["RETENTION"] = parse_boolean(value)

        elif key == "autoBackup":
            result["AUTO_BACKUP"] = parse_boolean(value)

        elif key == "maxSize":
            max_size_bytes = parse_integer(value)

            result["MAX_SIZE_BYTES"] = max_size_bytes

            if max_size_bytes is not None and max_size_bytes > 0:
                result["MAX_SIZE_CONFIGURED"] = True
                result["MAX_SIZE_MB"] = round(
                    max_size_bytes / (1024 * 1024),
                    2
                )

    return result


def parse_boolean(value: str) -> bool | None:
    """
    Convert a text Boolean value into a Python Boolean.

    Returns None when the value is not recognized.
    """

    normalized_value = value.strip().lower()

    if normalized_value == "true":
        return True

    if normalized_value == "false":
        return False

    return None


def parse_integer(value: str) -> int | None:
    """
    Convert a text value into an integer.

    Returns None when conversion fails.
    """

    try:
        return int(value.strip())
    except (ValueError, TypeError):
        return None